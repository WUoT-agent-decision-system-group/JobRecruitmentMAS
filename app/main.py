from collections import defaultdict

import spade
from agents.ApplicationAnalyzerAgent import ApplicationAnalyzerAgent
from agents.JobOfferManagerAgent import JobOfferManagerAgent
from agents.NotificationAgent import NotificationAgent
from agents.RecruiterAgent import RecruiterAgent
from dataaccess.model.JobOffer import JobOffer
from modules.JobOfferModule import JobOfferModule
from utils.log_config import LogConfig

from app.utils.configuration import MASConfiguration


async def create_agents(
    jobOffers: list[JobOffer], config: MASConfiguration
) -> list[spade.agent.Agent]:
    recruiter_offers_map = defaultdict(list)
    for jobOffer in jobOffers:
        recruiter_offers_map[jobOffer.recruiter_id].append(jobOffer.id)

    agents = [JobOfferManagerAgent(x.id) for x in jobOffers]

    for index in range(
        1, config.agents[ApplicationAnalyzerAgent.__name__].defined_instances + 1
    ):
        agents.append(ApplicationAnalyzerAgent(index))

    for index in range(
        1, config.agents[NotificationAgent.__name__].defined_instances + 1
    ):
        agents.append(NotificationAgent(index))

    for recruiter_id, offers_id in recruiter_offers_map.items():
        agents.append(RecruiterAgent(recruiter_id, offers_id))

    for a in agents:
        await a.start()

    return agents


async def main():
    logger = LogConfig.get_logger("init")
    config = MASConfiguration.load()
    dbname = config.agents[JobOfferManagerAgent.__name__].dbname
    jobOffers = JobOfferModule(dbname, logger).find_all()
    agents = await create_agents(jobOffers, config)
    await spade.wait_until_finished(agents)


if __name__ == "__main__":
    spade.run(main())
