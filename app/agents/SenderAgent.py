from spade.behaviour import CyclicBehaviour
from spade.message import Message

from .base.BaseAgent import BaseAgent


class SenderAgent(BaseAgent):
    class SendMessageBehaviour(CyclicBehaviour):
        async def run(self):
            self.agent.logger.info(
                "Sending message: Hello from SenderAgent!")
            msg = Message(to="receiver@aasd_server")  # Receiver's JID
            msg.set_metadata("performative", "inform")
            msg.body = "Hello from SenderAgent!"
            await self.send(msg)
            self.agent.logger.info("Message sent, stopping agent.")
            await self.agent.stop()

    async def setup(self):
        await super().setup()
        self.add_behaviour(self.SendMessageBehaviour())
