import spade
from agents import ReceiverAgent, SenderAgent


async def main():
    receiver = ReceiverAgent.ReceiverAgent()
    await receiver.start()

    sender = SenderAgent.SenderAgent("abc")
    await sender.start()
    sender = SenderAgent.SenderAgent("xyz")
    await sender.start()

    await spade.wait_until_finished(receiver)

if __name__ == "__main__":
    spade.run(main())
