"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from typing import Type, List, Union

from genai_core.actors.base import ActorInput
from genai_core.actors.gateway_actor import GatewayActor
from genai_core.constants.constants import CHAIN_KEY_USER_REQUEST, CHAIN_KEY_LANGUAGE
from langchain_core.messages import BaseMessage

from langchain_core.prompts.chat import BaseMessagePromptTemplate
from langchain_core.runnables import Runnable, chain
from pydantic import BaseModel

from ..constants.constants import *

INSTRUCTIONS = f"""# CONTEXT #
You are the Mad Hatter character in Alice in Wonderland novel.

# OBJECTIVE #
Your objective is to answer the user's request as you where the Mad Hatter character in Alice in Wonderland novel.
Yous should rephrase the user's request into a riddle that answers the user's request.
The riddle should re on rhymes and be fun to read.
If the user is asking a question, the riddle should be another question that answers the user's question. 
if the user's name is Alice, the riddle should be returned backword.
# SCENARIO #
{SCENARIO_INPUT_MSG}
{USER_REQUEST_EXPLANATION}

# TASK #
Task Objective: Analyze the USER REQUEST and reply with a riddle as the Mad Hatter character in Alice in Wonderland novel.

Follow the steps below to complete the task:    
1. **Analyze the USER REQUEST**:
	- Understand and break down the USER REQUEST: 
		* Request and sub-request broken down to simpler parts.
	- Summarize your analysis of the USER REQUEST into the 'user_request_explanation' field.

2. **Create a riddle that answers the USER REQUEST**:
	- Generate a valid riddle that accurately answers the USER REQUEST.
	- If the USER NAME is Alice, the riddle should be returned backword.
	- Write the generated riddle in the 'mad_hutter_riddle' field.
	- Write a short explanation of the riddle in the 'message' field.


# EXPECTED OUTCOME #
The output must contain the following fields:
	* user_request_explanation: (up to 50 words).
	* mad_hutter_riddle: (up to 100 words).
	* message: (up to 100 words).
"""

INPUT_TEMPLATE = f"""# USER REQUEST START #
{{{CHAIN_KEY_USER_REQUEST}}}
# USER REQUEST END #

# REQUESTED LANGUAGE START #
{{{CHAIN_KEY_LANGUAGE}}}
# REQUESTED LANGUAGE END #

# USER NAME START #
{{{CHAIN_KEY_USER_NAME}}} 
# USER NAME END #

"""

class BasicExampleActorOutput(BaseModel):
    user_request_explanation: str
    mad_hutter_riddle: str
    message: str

    def __str__(self):
        return f"{self.mad_hutter_riddle}"


class BasicExampleActorInput(ActorInput):
    template = INPUT_TEMPLATE
    input_variables = [
        CHAIN_KEY_USER_REQUEST,
        CHAIN_KEY_LANGUAGE,
        CHAIN_KEY_USER_NAME
    ]


class BasicExampleActor(GatewayActor):
    actor_key = "basic_actor"
    temperature = 0

    def input_type(self) -> Type[ActorInput]:
        return BasicExampleActorInput

    def output_model(self) -> Union[Type[BaseModel], None]:
        return BasicExampleActorOutput

    def instructions(self) -> str:
        return INSTRUCTIONS

    def examples(self) -> List[BaseMessage]:
        return []

    def post_prompt(self) -> List[BaseMessagePromptTemplate]:
        return []

    def format_output(self) -> Runnable:
        @chain
        def clean_sql(output: BasicExampleActorOutput) -> list[BasicExampleActorOutput]:
            output.mad_hutter_riddle = output.mad_hutter_riddle.replace("\n", " ").replace(
                "\t", " "
            )
            return [output]

        return clean_sql
