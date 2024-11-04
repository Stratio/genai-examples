"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import prometheus_client
import pytest

from genai_core.test.pytest_utils import setup_test_envs, reset_prometheus_registry

from genai_chain_metrics.chain import MetricsChain


class TestMetricsChain:
    def test_chain_input_schema(self, setup_test_envs, reset_prometheus_registry):
        genai_chain = MetricsChain()
        genai_chain.init_metrics()
        chain = genai_chain.chain()

        assert chain.input_schema.schema() == {"title": "RunnablePassthroughInput"}

    def test_chain_config_schema(self, setup_test_envs, reset_prometheus_registry):
        genai_chain = MetricsChain()
        genai_chain.init_metrics()
        chain = genai_chain.chain()

        assert chain.config_schema().schema() == {
            "properties": {},
            "title": "RunnableSequenceConfig",
            "type": "object",
        }

    def test_chain_output_schema(self, setup_test_envs, reset_prometheus_registry):
        genai_chain = MetricsChain()
        genai_chain.init_metrics()
        chain = genai_chain.chain()

        assert chain.output_schema().schema() == {
            "title": "increase_metric_output",
            "type": "object",
        }

    def test_chain_invoke(self, setup_test_envs, reset_prometheus_registry):
        genai_chain = MetricsChain()
        genai_chain.init_metrics()
        chain = genai_chain.chain()
        result = chain.invoke("hello")

        assert result == {"input": "hello"}

    def test_chain_metrics(self, setup_test_envs, reset_prometheus_registry):
        genai_chain = MetricsChain()
        genai_chain.init_metrics()
        chain = genai_chain.chain()
        # make two calls to generate the custom metrics
        chain.invoke("hello")
        chain.invoke("hello")

        # check the custom metrics
        metrics = list(prometheus_client.REGISTRY.collect())
        assert len(metrics) == 11
        invoke_metric = metrics[-1]
        assert invoke_metric.samples[0].name == "invoke_counter"
        assert invoke_metric.samples[0].value == 2.0


if __name__ == "__main__":
    pytest.main()
