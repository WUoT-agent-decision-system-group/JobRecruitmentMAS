import spade.behaviour

from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent


class RecruitmentStageManagerAgent(BaseAgent):
    def __init__(
        self, recruitment_id: str, identifier: int, recruitment_stage_attr: dict
    ):
        super().__init__(str.join("_", [recruitment_id, str(identifier)]))

        self.recruitment_id = recruitment_id
        self.recruitment_stage_attr = recruitment_stage_attr
        self.recruitment_stage_module = RecruitmentStageModule(
            self.agent_config.dbname, self.logger
        )
        self.recruitment_stage: RecruitmentStage = None

        # behaviours
        self.prepare_recruitment_stage_behav: PrepareRecruitmentStage = None

    async def setup(self):
        await super().setup()

        self.prepare_recruitment_stage_behav = PrepareRecruitmentStage()

        self.add_behaviour(self.prepare_recruitment_stage_behav)


class PrepareRecruitmentStage(spade.behaviour.OneShotBehaviour):

    agent: RecruitmentStageManagerAgent

    async def run(self):
        await self.create_recruitment_stage()
        self.agent.logger.info(self.agent.recruitment_stage_attr)

    async def create_recruitment_stage(self):
        self.agent.recruitment_stage_attr.update(
            {"_id": "", "recruitment_id": self.agent.recruitment_id}
        )
        self.agent.recruitment_stage = RecruitmentStage(
            **self.agent.recruitment_stage_attr
        )

        id = self.agent.recruitment_stage_module.create(self.agent.recruitment_stage)
        self.agent.recruitment_stage._id = id
