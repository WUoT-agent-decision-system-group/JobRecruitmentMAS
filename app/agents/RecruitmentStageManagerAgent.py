import spade.behaviour
from spade.message import Message

from app.dataaccess.model.RecruitmentStage import (
    RecruitmentStage,
    RecruitmentStageStatus,
)
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent


class RecruitmentStageManagerAgent(BaseAgent):
    def __init__(
        self,
        rm_jid: str,
        recruitment_id: str,
        identifier: int,
        recruitment_stage_attr: dict,
    ):
        super().__init__(str.join("_", [recruitment_id, str(identifier)]))

        self.rm_jid = rm_jid
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
        self.manage_stage_behav: ManageState = None

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

        self.agent.manage_stage_behav = ManageState(period=10)
        self.agent.add_behaviour(self.agent.manage_stage_behav)

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


class ManageState(spade.behaviour.PeriodicBehaviour):
    """Behaviour representing ManageStage protocol (mainly, asking RM agent for the permission to start)"""

    agent: RecruitmentStageManagerAgent

    async def run(self):
        self.agent.logger.info("ManageStage behaviour run.")

        await self.send_and_receive_instruction()

    async def send_and_receive_instruction(self):
        msg = await self.agent.prepare_message(
            self.agent.rm_jid,
            ["request"],
            ["start_request"],
            f"{self.agent.jid}%{self.agent.recruitment_stage.priority}",
        )

        self.agent.logger.info("Sending message to rm agent with the request to start.")
        await self.send(msg)

        msg = await self.receive(timeout=10)
        if msg is None:
            return

        start_allowed = await self.evaluate_stage_start(msg.body)
        if start_allowed:
            self.kill()

    async def evaluate_stage_start(self, body: str) -> bool:
        start_allowed = True if body == "True" else False
        self.agent.logger.info(
            f"Received message from rm agent with permission to start: {start_allowed}."
        )

        if start_allowed:
            self.agent.recruitment_stage.status = RecruitmentStageStatus.IN_PROGRESS
            self.agent.recruitment_stage_module.update(
                self.agent.recruitment_stage._id, {"status": 2}
            )

        return start_allowed
