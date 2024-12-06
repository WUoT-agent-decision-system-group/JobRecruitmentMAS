import spade.behaviour

from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent


class RecruitmentStageManagerAgent(BaseAgent):
    def __init__(
        self,
        recruitment_id: str,
        identifier: int,
        recruitment_stage_attr: dict,
    ):
        super().__init__(str.join("_", [recruitment_id, str(identifier)]))

        self.recruitment_id = recruitment_id
        self.identifier = identifier
        self.recruitment_stage_attr = recruitment_stage_attr
        self.recruitment_stage_module = RecruitmentStageModule(
            self.agent_config.dbname, self.logger
        )
        self.if_created = False
        self.recruitment_stage: RecruitmentStage = None

        # behaviours
        self.check_recruitment_stages_behav: CheckRecruitmentStages = None
        self.prepare_recruitment_stage_behav: PrepareRecruitmentStage = None

    async def setup(self):
        await super().setup()

        self.check_recruitment_stages_behav = CheckRecruitmentStages()

        self.add_behaviour(self.check_recruitment_stages_behav)


class CheckRecruitmentStages(spade.behaviour.OneShotBehaviour):
    """Checks whether recruitment stages with given recruitment_id and identifier are present in db"""

    agent: RecruitmentStageManagerAgent

    async def run(self):
        self.agent.logger.info("CheckRecruitmentStages behaviour run.")

        await self.check_recruitment_stages()

        self.agent.prepare_recruitment_stage_behav = PrepareRecruitmentStage()
        self.agent.add_behaviour(self.agent.prepare_recruitment_stage_behav)

    async def check_recruitment_stages(self):
        recruitment_stages = (
            self.agent.recruitment_stage_module.get_by_recruitment_and_identifier(
                self.agent.recruitment_id, self.agent.identifier
            )
        )

        if len(recruitment_stages) == 0:
            self.agent.if_created = False
            self.agent.logger.info(
                f"No recruitment stages found. Recruitment stage with recruitment: {self.agent.recruitment_id} and identifier: {self.agent.identifier} to be created."
            )
        else:
            self.agent.if_created = True
            self.agent.recruitment_stage = recruitment_stages[0]
            self.agent.logger.info(
                f"Found recruitment stage with id: {recruitment_stages[0]._id}. No recruitment stage objects will be created."
            )


class PrepareRecruitmentStage(spade.behaviour.OneShotBehaviour):
    """Creates recruitment stage object (if not present)"""

    agent: RecruitmentStageManagerAgent

    async def run(self):
        self.agent.logger.info("PrepareRecruitmentStage behaviour run.")

        await self.create_recruitment_stage()

    async def create_recruitment_stage(self):
        if self.agent.if_created:
            return

        self.agent.recruitment_stage_attr.update(
            {"_id": "", "recruitment_id": self.agent.recruitment_id}
        )
        self.agent.recruitment_stage = RecruitmentStage(
            **self.agent.recruitment_stage_attr
        )

        id = self.agent.recruitment_stage_module.create(self.agent.recruitment_stage)
        self.agent.recruitment_stage._id = id
