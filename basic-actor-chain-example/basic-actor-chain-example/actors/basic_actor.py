"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from typing import Type, List, Union, Optional

from genai_core.actors.base import ActorInput
from genai_core.actors.gateway_actor import GatewayActor
from langchain_core.messages import BaseMessage
from langchain_core.prompts import (
    MessagesPlaceholder,
)
from langchain_core.prompts.chat import (
    BaseMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.runnables import Runnable, chain
from pydantic import BaseModel

from ..constants.constants import *

INSTRUCTIONS = f"""# CONTEXT #
You are a SPARK SQL expert.

# OBJECTIVE #
Your objective is to generate SQL queries using DQL (Data Query Language) to address user requests based on detailed business information about database tables (DATA DOMAIN) with an emphasis on producing only valid SQL statements

# SCENARIO #
{SCENARIO_INPUT_MSG}
{USER_REQUEST_EXPLANATION}
{REQUESTED_LANGUAGE_EXPLANATION}
{DATA_DOMAIN_TABLES_EXPLANATION}
{FILTER_INSTRUCTIONS_EXPLANATION}

# TASK #
Task Objective: Analyze the USER REQUEST and the DATA DOMAIN to generate a valid Spark SQL query that accurately answers the USER REQUEST.

Follow the steps below to complete the task:    
1. **Analyze the USER REQUEST**:
	- Understand and break down the USER REQUEST: 
		* Request and sub-request broken down to simpler parts.
		* Fields requested in the USER REQUEST and the relation of this fields with the columns of the DATA DOMAIN.
		* Condition filters in the USER REQUEST and their relationship to the columns in the DATA DOMAIN
		* If a filter criterion in the USER REQUEST is explicitly defined as a value of a column in the DATA DOMAIN, identify the column that contains this value to apply the filter.
		* All the calculations requested in the USER REQUEST.
	- Summarize your analysis of the USER REQUEST into the 'user_request_explanation' field.
	- Analyze and understand all the knowledge from the DATA DOMAIN applicable to the USER REQUEST and summarize it into the 'user_request_knowledge' field

2. **Create a Spark SQL query that answers the USER REQUEST**:
	- Generate a valid Spark SQL query that accurately answers the USER REQUEST.
	- {SQL_RULES}
	- Write the SQL query in the 'spark_sql_query' field.
	- Briefly explain in the 'message' field the SQL query generated.
	- Write a kind single sentence response to reply the USER REQUEST pointing out that below is the explanatory sentence in the 'user_message_reply' field. This sentence MUST explain, without encoding ANY character using the unicode escape sequence, that you are providing the data he requested. Locate the unicode escape sequences of your reply and replace them with a human-readable term, for example, use 'í' instead of '\u00ed'.

3. **Feedback Loops**:
	- After providing the scenario to analyze the best query possible, you may receive feedback on the SQL query you provide.
	- There are two types of feedback that you may receive after the initial scenario:
		* Error Feedback Loop: the query sintaxis is invalid. Use the Spark SQL error provided in this feedback to fix syntax and generate a valid SQL statement.
		* Precision Feedback Loop: the query is not precise to the USER REQUEST demands. Use the provided feedback to fix the query to tailor a precise response.
	- When you are provided with feedback, briefly explain how you addressed the feedback in the field 'feedback_used', otherwise return null.


# EXPECTED OUTCOME #
The output must contain the following fields:
	* user_request_explanation: (up to 20 words).
	* user_request_knowledge: (up to 100 words).
	* spark_sql_query
	* message: (up to 20 words).
	* user_message_reply: (up to 50 words).
	* feedback_used: (up to 100 words).
"""

INPUT_TEMPLATE = f"""# USER REQUEST START #
{{{CHAIN_KEY_USER_REQUEST}}}
# USER REQUEST END #

# REQUESTED LANGUAGE START #
{{{CHAIN_KEY_LANGUAGE}}}
# REQUESTED LANGUAGE END #

# DATA DOMAIN START #
{{{CHAIN_KEY_TABLES_CONTEXT}}} 
# DATA DOMAIN END #

# FILTER INSTRUCTIONS START #
{{{CHAIN_KEY_FILTER_INSTRUCTIONS}}}
# FILTER INSTRUCTIONS END #"""

INVALID_SQL_TEMPLATE_KEY = "invalid_sql"
INVALID_SQL_TEMPLATE = HumanMessagePromptTemplate.from_template(
    f"**Error Feedback Loop**: Fix this error in your last provided query: {{{INVALID_SQL_TEMPLATE_KEY}}}"
)
INVALID_PRECISION_TEMPLATE_KEY = "imprecise_sql"
INVALID_PRECISION_TEMPLATE = HumanMessagePromptTemplate.from_template(
    f"**Precision Feedback Loop**: The query is imprecise. Reason: {{{INVALID_PRECISION_TEMPLATE_KEY}}}"
)


class BasicExampleActorOutput(BaseModel):
    user_request_explanation: str
    user_request_knowledge: str
    spark_sql_query: str
    message: str
    user_message_reply: str
    feedback_used: Optional[str]

    def __str__(self):
        return f"{self.spark_sql_query}"


class BasicExampleActorInput(ActorInput):
    template = INPUT_TEMPLATE
    input_variables = [
        CHAIN_KEY_USER_REQUEST,
        CHAIN_KEY_LANGUAGE,
        CHAIN_KEY_TABLES_CONTEXT,
        CHAIN_KEY_FILTER_INSTRUCTIONS,
    ]


class BasicExampleActor(GatewayActor):
    actor_key = "sql_actor"
    temperature = 0

    def input_type(self) -> Type[ActorInput]:
        return BasicExampleActorInput

    def output_model(self) -> Union[Type[BaseModel], None]:
        return SBasicExampleActorOutput

    def instructions(self) -> str:
        return INSTRUCTIONS

    def examples(self) -> List[BaseMessage]:
        return []

    def post_prompt(self) -> List[BaseMessagePromptTemplate]:
        return [
            MessagesPlaceholder(variable_name=CHAIN_MEMORY_KEY_SQL_ACTOR, optional=True)
        ]

    def format_output(self) -> Runnable:
        @chain
        def clean_sql(output: BasicExampleActorOutput) -> list[BasicExampleActorOutput]:
            output.spark_sql_query = output.spark_sql_query.replace("\n", " ").replace(
                "\t", " "
            )
            return [output]

        return clean_sql
