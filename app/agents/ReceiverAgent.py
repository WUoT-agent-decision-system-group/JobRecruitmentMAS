from spade.behaviour import CyclicBehaviour

from .BaseAgent import BaseAgent


class ReceiverAgent(BaseAgent):

    class ReceiveMessageBehaviour(CyclicBehaviour):

        async def run(self):
            # Wait for a message for up to 10 seconds
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.logger.info("Received message: %s", msg.body)
            else:
                self.agent.logger.info(
                    "No message received within the timeout.")

    async def setup(self):
        await super().setup()
        self.add_behaviour(self.ReceiveMessageBehaviour())
