import logging
from abc import ABC
from time import sleep

from spade.agent import Agent
from utils.configuration import MASConfiguration
from utils.log_config import LogConfig


class BaseAgent(ABC, Agent):
    def __init__(self):

        # tigase config
        config = MASConfiguration.load()
        self.agent_config = config.agents[self.__class__.__name__]
        jid = self.agent_config.jid + "@" + config.server.name
        super().__init__(jid, self.agent_config.password)

        self.id = self.agent_config.jid

        # logger config
        LogConfig.load_config(self.id)
        self.logger = logging.getLogger(f"Agent.{self.id}")
        self.logger.info("Logger initialized for %s", self.id)

    async def start(self, auto_register: bool = True) -> None:
        """Waits for server to initialize"""

        repeat = True
        while repeat is True:
            try:
                await super().start(auto_register)
                repeat = False

                # pylint: disable=W0718
            except Exception:
                self.logger.error('Server not found, trying again...')
                sleep(3)
                repeat = True

    async def setup(self):
        self.logger.info("setup - started")
