from abc import ABC
from time import sleep
from typing import List, Tuple

from aioxmpp import JID
from spade.agent import Agent
from spade.message import Message

from app.dataaccess.model.MessageType import MessageType
from app.utils.configuration import MASConfiguration
from app.utils.log_config import LogConfig

DATA_SEPARATOR = "%"


class BaseAgent(ABC, Agent):
    def __init__(self, custom_id: str = ""):

        # tigase config
        config = MASConfiguration.load()
        self.agent_config = config.agents[self.__class__.__name__]
        self.id = self.agent_config.jid
        self.cid = custom_id
        if custom_id != "":
            self.id += f"_{custom_id}"

        jid = self.id + "@" + config.server.name
        super().__init__(jid, self.agent_config.password)

        # logger config
        self.logger = LogConfig.get_logger(f"Agent.{self.id}")

    async def start(self, auto_register: bool = True) -> None:
        """Waits for server to initialize"""

        repeat = True
        while repeat is True:
            try:
                await super().start(auto_register)
                repeat = False

                # pylint: disable=W0718
            except Exception:
                self.logger.error("Server not found, trying again...")
                sleep(3)
                repeat = True

    async def stop(self):
        if not self.is_alive():
            self.logger.info("STOP\n")
        return await super().stop()

    async def setup(self):
        self.logger.info("setup - started")

    async def prepare_message(
        self,
        to_jid: JID,
        performative: str,
        ontology: str,
        type: MessageType,
        data: List[str],
    ) -> Message:
        self.logger.info(f"Preparing message to agent with jid: {str(to_jid)}")
        msg = Message(to=str(to_jid))

        msg.set_metadata("performative", performative)
        msg.set_metadata("ontology", ontology)

        data.insert(0, str(type.value))
        msg.body = DATA_SEPARATOR.join(data)
        return msg

    async def get_message_type_and_data(
        self, msg: Message
    ) -> Tuple[MessageType, List[str]]:
        data = msg.body.split(DATA_SEPARATOR)

        return MessageType(int(data[0])), data[1:]
