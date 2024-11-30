from spade.behaviour import CyclicBehaviour

from app.modules.TestModule import TestModule

from .base.BaseAgent import BaseAgent


class ReceiverAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.test_module = TestModule(self.agent_config.dbname, self.logger)

    class ReceiveMessageBehaviour(CyclicBehaviour):

        async def run(self):
            # Wait for a message for up to 10 seconds
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.logger.info("Received message: %s", msg.body)
            else:
                self.agent.logger.info("No message received within the timeout, stopping agent.")
                await self.agent.stop()

    async def setup(self):
        await super().setup()
        self.add_behaviour(self.ReceiveMessageBehaviour())
