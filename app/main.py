import spade
from agents.JobOfferManagerAgent import JobOfferManagerAgent
from dataaccess.model.JobOffer import JobOffer
from modules.JobOfferModule import JobOfferModule
from utils.log_config import LogConfig

from app.utils.configuration import MASConfiguration


def get_module() -> JobOfferModule:
    logger = LogConfig.get_logger('init')
    config = MASConfiguration.load()
    dbname = config.agents[JobOfferManagerAgent.__name__].dbname
    return JobOfferModule(dbname, logger)


async def create_agents(jobOffers: list[JobOffer]) -> list[spade.agent.Agent]:
    agents = [JobOfferManagerAgent(x.id) for x in jobOffers]

    for a in agents:
        await a.start()

    return agents


async def main():
    module = get_module()
    jobOffers = module.get_open_job_offers()

    agents = await create_agents(jobOffers)
    await spade.wait_until_finished(agents)

if __name__ == "__main__":
    spade.run(main())
