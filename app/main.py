from agents import ReceiverAgent, SenderAgent


async def main():
    receiver = ReceiverAgent.ReceiverAgent(
        "receiver@server_hello", "receiver_password")
    await receiver.start()

    sender = SenderAgent.SenderAgent("sender@server_hello", "sender_password")
    await sender.start()

    # Wait for SenderAgent to complete sending the message
    # await sender.()

    # Stop the receiver after processing messages
    await receiver.stop()

if __name__ == "__main__":
    import spade
    spade.run(main())
