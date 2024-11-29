from agents import ReceiverAgent, SenderAgent


async def main():
    receiver = ReceiverAgent.ReceiverAgent()
    await receiver.start()

    sender = SenderAgent.SenderAgent("abc")
    await sender.start()
    sender = SenderAgent.SenderAgent("xyz")
    await sender.start()

    # Wait for SenderAgent to complete sending the message
    # await sender.()

    # Stop the receiver after processing messages
    await receiver.stop()

if __name__ == "__main__":
    import spade
    spade.run(main())
