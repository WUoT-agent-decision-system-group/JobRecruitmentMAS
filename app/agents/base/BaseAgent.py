from abc import ABC
from time import sleep

from spade.agent import Agent

from app.utils.configuration import MASConfiguration
from app.utils.log_config import LogConfig


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
