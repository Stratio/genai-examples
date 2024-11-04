"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from locust import HttpUser, task, between


class EchoChainUser(HttpUser):
    """
    This is a performance test for the echo chain.
    install
      -> pip3 install locust
    run basic test
      -> locust --users 10 --spawn-rate 1 --host http://127.0.0.1:8080 --modern-ui
    """

    wait_time = between(1, 20)

    @task
    def invoke(self):
        self.client.post(
            "/v1/chains/chain_echo/invoke",
            json={
                "input": "Hello",
                "config": {"configurable": {}, "metadata": {}},
            },
        )
