import spade.behaviour

from app.agents.RecruitmentManagerAgent import RecruitmentManagerAgent
from app.dataaccess.model.JobOffer import ApplicationDetails, ApplicationStatus
from app.modules.JobOfferModule import JobOfferModule

from .base.BaseAgent import BaseAgent


class JobOfferManagerAgent(BaseAgent):
    def __init__(self, job_offer_id):
        super().__init__(job_offer_id)
        self.jobOfferModule = JobOfferModule(self.agent_config.dbname, self.logger)
        self.job_offer_id = job_offer_id
        self.jobOffer = None
        self.applications: list[ApplicationDetails] = None
        self.new_applications: list[ApplicationDetails] = []
        self.recruitments: list[RecruitmentManagerAgent] = []

        # behaviours
        self.processCandidateBehav = self.ProcessCandidateBehaviour()
        self.initRmentsBehav = self.InitRecruitments()

    async def setup(self):
        await super().setup()

        self.jobOffer = self.jobOfferModule.get(self.job_offer_id)
        if self.jobOffer is None:
            self.logger.error("Job offer not found.")
            await self.stop()

        self.applications = [x for x in self.jobOffer.applications
                             if x.status != ApplicationStatus.NEW]
        self.new_applications = [x for x in self.jobOffer.applications
                                 if x.status == ApplicationStatus.NEW]

        self.add_behaviour(self.processCandidateBehav)
        self.add_behaviour(self.initRmentsBehav)

    class InitRecruitments(spade.behaviour.OneShotBehaviour):

        async def run(self):
            for appl in self.agent.applications:
                self.agent.logger.info("Starting RmentAgent for job '%s', candidate '%s'",
                                       self.agent.jobOffer.id, appl.candidate_id)
                rment_agent = RecruitmentManagerAgent(self.agent.jobOffer.id, appl.candidate_id)
                self.agent.recruitments.append(rment_agent)
                await rment_agent.start()
            await self.agent.stop()

    class ProcessCandidateBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self):
            pass
            # TODO
            # await self.agent.stop()
