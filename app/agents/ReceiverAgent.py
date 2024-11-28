from spade.behaviour import CyclicBehaviour

from .BaseAgent import BaseAgent


class ReceiverAgent(BaseAgent):

    class ReceiveMessageBehaviour(CyclicBehaviour):

        async def run(self):
            # Wait for a message for up to 10 seconds
            msg = await self.receive(timeout=10)
            if msg:
                print(f"[receiver] Received message: {msg.body}")
            else:
                print("[receiver] No message received within the timeout.")

    async def setup(self):
        print(f"ReceiverAgent {self.jid} started")
        self.add_behaviour(self.ReceiveMessageBehaviour())

    def tolog(self):
        pass
