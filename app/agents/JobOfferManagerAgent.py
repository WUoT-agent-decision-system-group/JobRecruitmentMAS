import spade.behaviour

from app.modules.JobOfferModule import JobOfferModule

from .base.BaseAgent import BaseAgent


class JobOfferManagerAgent(BaseAgent):
    def __init__(self, job_offer_id):
        super().__init__(job_offer_id)
        self.jobOfferModule = JobOfferModule(self.agent_config.dbname, self.logger)
        self.jobOffer = self.jobOfferModule.get(job_offer_id)
        self.applications = self.jobOffer.applications

        # behaviours
        self.processCandidateBehav = self.ProcessCandidateBehaviour()

    async def setup(self):
        await super().setup()
        self.add_behaviour(self.processCandidateBehav)

    class ProcessCandidateBehaviour(spade.behaviour.OneShotBehaviour):
        async def run(self):
            # TODO
            await self.agent.stop()
