from abc import ABC, abstractmethod
from time import sleep

from spade.agent import Agent
from utils import configuration as cfg


class BaseAgent(ABC, Agent):
    def __init__(self):
        config = cfg.MASConfiguration.load()
        agent_config = config.agents[self.__class__.__name__]
        jid = agent_config.jid + "@" + config.server.name
        super().__init__(jid, agent_config.password)

    async def start(self, auto_register: bool = True) -> None:
        """Waits for server to initialize"""

        repeat = True
        while repeat is True:
            try:
                await super().start(auto_register)
                repeat = False
            except Exception:
                print('Server not found, trying again...')
                sleep(3)
                repeat = True

    @abstractmethod
    def tolog(self):
        pass
