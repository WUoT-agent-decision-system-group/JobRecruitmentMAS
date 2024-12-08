from typing import Type

import spade.behaviour
from spade.message import Message

from app.dataaccess.model.Recruitment import Recruitment
from app.dataaccess.model.RecruitmentInstruction import RecruitmentInstruction
from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.modules.RecruitmentInstructionModule import RecruitmentInstructionModule
from app.modules.RecruitmentModule import RecruitmentModule
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent
from .RecruitmentStageManagerAgent import RecruitmentStageManagerAgent


class RecruitmentManagerAgent(BaseAgent):
    def __init__(self, job_offer_id: str, candidate_id: str):
        super().__init__(str.join("_", [job_offer_id, candidate_id]))

        self.job_offer_id = job_offer_id
        self.candidate_id = candidate_id
        self.recruitment_module = RecruitmentModule(
            self.agent_config.dbname, self.logger
        )
        self.recruitment_instruction_module = RecruitmentInstructionModule(
            self.agent_config.dbname, self.logger
        )
        self.if_created = False
        self.recruitment: Recruitment = None
        self.recruitment_instruction: RecruitmentInstruction = None

        # behaviours
        self.check_recruitments_behav: CheckRecruitments = None
        self.prepare_recruitment_behav: PrepareRecruitment = None
        self.stage_communication_behav: StageCommunication = None

    async def setup(self):
        await super().setup()

        self.check_recruitments_behav = CheckRecruitments()
        self.stage_communication_behav = StageCommunication()

        self.add_behaviour(self.check_recruitments_behav)
        self.add_behaviour(self.stage_communication_behav)


class CheckRecruitments(spade.behaviour.OneShotBehaviour):
    """Checks whether recruitments with given job_offer_id, candidate_id and required stages are present in db"""

    agent: RecruitmentManagerAgent

    async def run(self):
        self.agent.logger.info("CheckRecruitments behaviour run.")

        await self.check_recruitments()

        self.agent.prepare_recruitment_behav = PrepareRecruitment()
        self.agent.add_behaviour(self.agent.prepare_recruitment_behav)

    async def check_recruitments(self):
        recruitments = self.agent.recruitment_module.get_by_job_and_candidate(
            self.agent.job_offer_id, self.agent.candidate_id
        )

        if len(recruitments) == 0:
            self.agent.if_created = False
            self.agent.logger.info(
                f"No recruitments found. Recruitment with job_offer_id: {self.agent.job_offer_id} and candidate_id: {self.agent.candidate_id} to be created."
            )
        else:
            self.agent.if_created = True
            self.agent.recruitment = recruitments[0]

            self.agent.logger.info(
                f"Found recruitment with id: {recruitments[0]._id}. No recruitment objects will be created."
            )


class PrepareRecruitment(spade.behaviour.OneShotBehaviour):
    """Creates recruitment object (if not present) and initiates RmentStageAgents (one per one stage)"""

    agent: RecruitmentManagerAgent

    async def run(self):
        self.agent.logger.info("PrepareRecruitment behaviour run.")

        await self.get_recruitment_instruction()
        await self.create_recruitment()
        await self.create_stage_agents()

    async def get_recruitment_instruction(self):
        self.agent.recruitment_instruction = (
            self.agent.recruitment_instruction_module.get_by_job_offer_id(
                self.agent.job_offer_id
            )
        )

    async def create_recruitment(self):
        if self.agent.if_created:
            return

        self.agent.recruitment = Recruitment(
            "", self.agent.job_offer_id, self.agent.candidate_id, 1
        )

        id = self.agent.recruitment_module.create(self.agent.recruitment)
        self.agent.recruitment._id = id

    async def create_stage_agents(self):
        for i in range(self.agent.recruitment_instruction.stages_number):
            recruitment_stage_attr = {
                "identifier": i,
                "status": 1,
                "type": self.agent.recruitment_instruction.stage_types[i].value,
                "priority": self.agent.recruitment_instruction.stage_priorities[i],
            }
            rment_stage_agent = RecruitmentStageManagerAgent(
                self.agent.jid,
                self.agent.recruitment._id,
                i,
                recruitment_stage_attr,
            )

            await rment_stage_agent.start()

            self.agent.logger.info(
                f"{i}) Started RSM agent for recruitment with id: {self.agent.recruitment._id}."
            )


class StageCommunication(spade.behaviour.CyclicBehaviour):
    """Behaviour representing ManageStageRequest and ManageStageResponse protocols"""

    agent: RecruitmentManagerAgent

    async def run(self):
        self.agent.logger.info("StageCommunication behaviour run.")

        await self.receive_and_send()

    async def receive_and_send(self):
        msg = await self.receive(timeout=10)
        if msg is None:
            return

        data = msg.body.split("%")
        self.agent.logger.info(f"Received message from rsm agent with jid: {data[0]}")

        start_permission = await self.validate_priority(int(data[1]))
        msg = await self.agent.prepare_message(
            data[0], ["response"], ["start_permission"], f"{start_permission}"
        )

        self.agent.logger.info(
            "Sending message to rsm agent with the start permission."
        )
        await self.send(msg)

    async def validate_priority(self, stage_priority: int) -> bool:
        return self.agent.recruitment.current_priority == stage_priority
