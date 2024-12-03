import spade.behaviour

from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent


class RecruitmentStageManagerAgent(BaseAgent):
    def __init__(self, recruitment_id: str, recruitment_stage: RecruitmentStage):
        super().__init__(str.join("_", [recruitment_id, recruitment_stage._id]))

        self.recruitment_stage: RecruitmentStage = recruitment_stage
        self.recruitment_id = recruitment_id
        self.recruitment_stage_module = RecruitmentStageModule(
            self.agent_config.dbname, self.logger
        )

        # behaviours
        self.test_behav: TestBehav = None

    async def setup(self):
        await super().setup()

        self.test_behav = TestBehav()

        self.add_behaviour(self.test_behav)


class TestBehav(spade.behaviour.OneShotBehaviour):

    agent: RecruitmentStageManagerAgent

    async def run(self):
        self.agent.logger.info(
            f"Hello from rmentStageAgent: {self.agent.recruitment_stage._id}"
        )
