from abc import ABC, abstractmethod
from time import sleep

from spade.agent import Agent


class BaseAgent(ABC, Agent):
    async def start(self, auto_register: bool = True) -> None:
        repeat = True
        while repeat is True:
            try:
                await super().start(auto_register)
                repeat = False
            except Exception:
                print('Server not found, trying again...')
                sleep(3)
                repeat = True

    def __init__(self, jid, password, verify_security=False):
        super().__init__(jid, password, verify_security)
        print(self.__class__.__name__)

    @abstractmethod
    def tolog(self):
        pass
