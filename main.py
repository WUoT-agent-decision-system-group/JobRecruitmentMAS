import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class ReceiverAgent(Agent):
    class ReceiveMessageBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Wait for a message for up to 10 seconds
            if msg:
                print(f"[receiver] Received message: {msg.body}")
            else:
                print("[receiver] No message received within the timeout.")

    async def setup(self):
        print(f"ReceiverAgent {self.jid} started")
        self.add_behaviour(self.ReceiveMessageBehaviour())


class SenderAgent(Agent):
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


async def main():
    receiver = ReceiverAgent("receiver@server_hello", "receiver_password")
    await receiver.start()

    # Wait for ReceiverAgent to initialize
    await asyncio.sleep(5)

    sender = SenderAgent("sender@server_hello", "sender_password")
    await sender.start()

    # Wait for SenderAgent to complete sending the message
    await sender.join()

    # Stop the receiver after processing messages
    await receiver.stop()

if __name__ == "__main__":
    import spade
    spade.run(main())
