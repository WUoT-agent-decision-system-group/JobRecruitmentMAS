import random

import spade.behaviour
from agents.NotificationAgent import NotificationAgent

from app.dataaccess.model.MessageType import MessageType
from app.dataaccess.model.RecruitmentStage import (
    RecruitmentStage,
    RecruitmentStageStatus,
)
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent

MANAGE_STAGE_PERIOD = 10
TRACK_STAGE_PERIOD = 20


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
        self.track_stage_behav: TrackStage = None

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
                "No recruitment stages found. Recruitment stage with recruitment: %s and identifier: %s to be created.",
                self.agent.recruitment_id,
                self.agent.identifier,
            )
        else:
            self.agent.if_created = True
            self.agent.recruitment_stage = recruitment_stages[0]

            await self.check_stage_status()
            self.agent.logger.info(
                "Found recruitment stage with id: %s. No recruitment stage objects will be created.",
                recruitment_stages[0]._id,
            )

    async def check_stage_status(self):
        if self.agent.recruitment_stage.status == RecruitmentStageStatus.DONE:
            self.agent.logger.info("Stage status is DONE. Exiting agent...")

            await self.agent.stop()


class PrepareRecruitmentStage(spade.behaviour.OneShotBehaviour):
    """Creates recruitment stage object (if not present)"""

    agent: RecruitmentStageManagerAgent

    async def run(self):
        self.agent.logger.info("PrepareRecruitmentStage behaviour run.")

        await self.create_recruitment_stage()

        self.agent.manage_stage_behav = ManageState(period=MANAGE_STAGE_PERIOD)
        self.agent.add_behaviour(self.agent.manage_stage_behav)

    async def create_recruitment_stage(self):
        if self.agent.if_created:
            return

        self.agent.recruitment_stage_attr.update(
            {"_id": "", "recruitment_id": self.agent.recruitment_id, "result": 0.0}
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

        await self.send_and_receive()

    async def send_and_receive(self):
        msg = await self.agent.prepare_message(
            self.agent.rm_jid,
            "request",
            "start_request",
            MessageType.START_REQUEST,
            [f"{self.agent.jid}", f"{self.agent.recruitment_stage.priority}"],
        )

        self.agent.logger.info("Sending message to rm agent with the request to start.")
        await self.send(msg)

        msg = await self.receive(timeout=10)
        if msg is None:
            return

        _, data = await self.agent.get_message_type_and_data(msg)
        start_allowed = await self.evaluate_stage_start(data[0])
        if start_allowed:
            self.agent.track_stage_behav = TrackStage(period=TRACK_STAGE_PERIOD)
            self.agent.add_behaviour(self.agent.track_stage_behav)

            self.kill()
            return

    async def evaluate_stage_start(self, body: str) -> bool:
        start_allowed = True if body == "True" else False
        self.agent.logger.info(
            "Received message from rm agent with permission to start: %s.",
            start_allowed,
        )

        if (
            start_allowed
            and self.agent.recruitment_stage.status == RecruitmentStageStatus.CREATED
        ):
            self.agent.recruitment_stage.status = RecruitmentStageStatus.IN_PROGRESS
            self.agent.recruitment_stage_module.update(
                self.agent.recruitment_stage._id,
                {"status": RecruitmentStageStatus.IN_PROGRESS.value},
            )
            prefix = self.agent.config.agents[
                NotificationAgent.__name__.split(".")[-1]
            ].jid
            instances = self.agent.config.agents[
                NotificationAgent.__name__.split(".")[-1]
            ].defined_instances

            msg = await self.agent.prepare_message(
                f"{prefix}_{random.randint(1, instances)}@{self.agent.config.server.name}",
                "request",
                "notif",
                MessageType.NOTIF_CANDIDATE_RMENT_REQUEST,
                [
                    f"{self.agent.recruitment_id}",
                    f"The stage of the type {self.agent.recruitment_stage.type} can be started!",
                ],
            )

            await self.send(msg)

            self.agent.logger.info(
                "Sent message to notification agent with the notif request."
            )

        return start_allowed


class TrackStage(spade.behaviour.PeriodicBehaviour):
    """Behaviour representing TrackStageProgress activity and SendStageResult protocol in order to send stage result when status is DONE"""

    agent: RecruitmentStageManagerAgent

    async def run(self):
        self.agent.logger.info("TrackStage behaviour run.")

        await self.check_stage_progress()

    async def check_stage_progress(self):
        self.agent.recruitment_stage = self.agent.recruitment_stage_module.get(
            self.agent.recruitment_stage._id
        )

        if self.agent.recruitment_stage.status == RecruitmentStageStatus.DONE:
            self.agent.logger.info("Stage has been completed.")
            await self.send_and_receive()
        else:
            self.agent.logger.info("Stage is in progress.")

    async def send_and_receive(self):
        msg = await self.agent.prepare_message(
            self.agent.rm_jid,
            "inform",
            "stage_result",
            MessageType.STAGE_RESULT,
            [f"{self.agent.jid}", f"{self.agent.recruitment_stage.result}"],
        )

        self.agent.logger.info("Sending message to rm agent with the stage result.")
        await self.send(msg)

        msg = await self.receive(timeout=10)
        if msg is None:
            return

        _, data = await self.agent.get_message_type_and_data(msg)
        if data[0] == "ACK":
            self.agent.logger.info(
                "Rment agent received stage result. Exiting agent..."
            )
            await self.agent.stop()
