from asyncio import sleep

import spade.behaviour

from app.agents.RecruitmentManagerAgent import RecruitmentManagerAgent
from app.dataaccess.model.JobOffer import (ApplicationDetails,
                                           ApplicationStatus, JobOffer)
from app.modules.JobOfferModule import JobOfferModule

from .base.BaseAgent import BaseAgent


class JobOfferManagerAgent(BaseAgent):
    def __init__(self, job_offer_id):
        super().__init__(job_offer_id)
        self.jobOfferModule = JobOfferModule(self.agent_config.dbname, self.logger)
        self.job_offer_id = job_offer_id
        self.jobOffer = None
        self.applications_to_init: list[ApplicationDetails] = None
        self.recruitments: list[RecruitmentManagerAgent] = []

        # behaviours
        self.processCandidateBehav: self.ProcessCandidateBehaviour = None
        self.initRmentsBehav: self.InitRecruitments = None
        self.awaitApplicationBehav: self.AwaitApplication = None

    async def setup(self):
        await super().setup()

        self.jobOffer = self.jobOfferModule.get(self.job_offer_id)
        if self.jobOffer is None:
            self.logger.error("Job offer not found.")
            await self.stop()

        self.applications_to_init = [x for x in self.jobOffer.applications
                                     if x.status != ApplicationStatus.NEW]

        self.initRmentsBehav = self.InitRecruitments()
        self.add_behaviour(self.initRmentsBehav)
        self.awaitApplicationBehav = self.AwaitApplication(period=5)
        self.add_behaviour(self.awaitApplicationBehav)

    class InitRecruitments(spade.behaviour.OneShotBehaviour):

        async def run(self):
            apps = self.agent.applications_to_init
            print(f"\n\nInit recruitments: {apps}\n\n")
            if apps is None:
                return

            self.agent.applications_to_init = None

            for app in apps:
                self.agent.logger.info("Starting RmentAgent for job '%s', candidate '%s'",
                                       self.agent.jobOffer.id, app.candidate_id)
                rment_agent = RecruitmentManagerAgent(self.agent.jobOffer.id, app.candidate_id)
                self.agent.recruitments.append(rment_agent)
                await rment_agent.start()

    class AwaitApplication(spade.behaviour.PeriodicBehaviour):

        async def run(self):
            jobOffer: JobOffer = self.agent.jobOfferModule.get(self.agent.job_offer_id)
            new_applications = [x for x in jobOffer.applications
                                if x.status == ApplicationStatus.NEW]

            # TODO zmienić status na PROCESSED

            # TODO wywołanie ProcessCandidateBehaviour
            # self.agent.processCandidateBehav = self.agent.ProcessCandidateBehav()
            # self.agent.add_behaviour(self.agent.processCandidateBehav)
            # self.agent.processCandidateBehav.join()

            # aplikacje juz nie w stanie new
            self.agent.applications_to_init = new_applications
            self.agent.initRmentsBehav = self.agent.InitRecruitments()
            self.agent.add_behaviour(self.agent.initRmentsBehav)

    class ProcessCandidateBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self):
            pass
            # TODO
            # await self.agent.stop()
