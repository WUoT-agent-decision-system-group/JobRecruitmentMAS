from spade.behaviour import CyclicBehaviour
from spade.message import Message

from .BaseAgent import BaseAgent


class SenderAgent(BaseAgent):
    class SendMessageBehaviour(CyclicBehaviour):
        async def run(self):
            print("[sender] Sending message: Hello from SenderAgent!")
            msg = Message(to="receiver@server_hello")  # Receiver's JID
            msg.set_metadata("performative", "inform")
            msg.body = "Hello from SenderAgent!"
            await self.send(msg)
            print("[sender] Message sent, stopping agent.")
            await self.agent.stop()

    async def setup(self):
        print(f"SenderAgent {self.jid} started")
        self.add_behaviour(self.SendMessageBehaviour())

    def tolog(self):
        pass
