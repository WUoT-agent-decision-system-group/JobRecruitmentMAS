import spade.behaviour

from app.modules.RecruitmentModule import RecruitmentModule

from .base.BaseAgent import BaseAgent


class RecruitmentManagerAgent(BaseAgent):
    def __init__(self, job_offer_id: str, candidate_id: str):
        super().__init__(str.join('_', [job_offer_id, candidate_id]))
        self.job_offer_id = job_offer_id
        self.candidate_id = candidate_id
        self.recruitmentModule = RecruitmentModule(self.agent_config.dbname, self.logger)
        self.recruitment = None

        # TODO behaviours

    async def setup(self):
        await super().setup()
        self.recruitment = self.recruitmentModule.get_stages_info(self.job_offer_id)
        if self.recruitment is None:
            await self.stop()

        # TODO
        # self.add_behaviour()
