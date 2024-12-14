import spade

from agents.JobOfferManagerAgent import JobOfferManagerAgent
from agents.ApplicationAnalyzerAgent import ApplicationAnalyzerAgent
from agents.RecruiterAgent import RecruiterAgent
from dataaccess.model.JobOffer import JobOffer
from modules.JobOfferModule import JobOfferModule
from utils.log_config import LogConfig
from collections import defaultdict

from app.utils.configuration import MASConfiguration

ANALYZER_INSTANCES = 2

def get_module() -> JobOfferModule:
    logger = LogConfig.get_logger("init")
    config = MASConfiguration.load()
    dbname = config.agents[JobOfferManagerAgent.__name__].dbname
    return JobOfferModule(dbname, logger)


async def create_agents(jobOffers: list[JobOffer]) -> list[spade.agent.Agent]:
    recruiter_offers_map = defaultdict(list)
    for jobOffer in jobOffers:
        recruiter_offers_map[jobOffer.recruiter_id].append(jobOffer.id)

    agents = [JobOfferManagerAgent(x.id, ANALYZER_INSTANCES) for x in jobOffers]

    for _ in range(0, ANALYZER_INSTANCES):
        agents.append(ApplicationAnalyzerAgent())

    for recruiter_id, offers_id in recruiter_offers_map.items():
        print(recruiter_id)
        print(offers_id)
        agents.append(RecruiterAgent(recruiter_id, offers_id))

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
