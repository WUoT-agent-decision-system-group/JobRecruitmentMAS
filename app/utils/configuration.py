import json
from dataclasses import dataclass
from typing import Dict

CONFIGFILE = "app/config.json"


@dataclass
class ServerConfig:
    name: str


@dataclass
class AgentConfig:
    jid: str
    password: str
    dbname: str
    defined_instances: int = None


@dataclass
class DBConfig:
    host: str


@dataclass
class MASConfiguration:
    server: ServerConfig
    agents: Dict[str, AgentConfig]
    db: DBConfig

    @staticmethod
    def load():
        with open(CONFIGFILE, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        server = ServerConfig(**config["server"])
        agents = {
            name: AgentConfig(**agent) for name, agent in config["agents"].items()
        }
        db = DBConfig(**config["db"])

        return MASConfiguration(server=server, agents=agents, db=db)
