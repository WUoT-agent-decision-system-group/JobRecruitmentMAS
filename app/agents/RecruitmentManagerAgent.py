import random
from typing import List, Optional

import spade.behaviour

from app.agents import NotificationAgent
from app.dataaccess.model.JobOffer import ApplicationStatus
from app.dataaccess.model.MessageType import MessageType
from app.dataaccess.model.Recruitment import Recruitment
from app.dataaccess.model.RecruitmentInstruction import RecruitmentInstruction
from app.dataaccess.model.RecruitmentStage import RecruitmentStageStatus
from app.modules.JobOfferModule import JobOfferModule
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
        self.jobOffer_module = JobOfferModule(self.agent_config.dbname, self.logger)
        self.recruitment_module = RecruitmentModule(
            self.agent_config.dbname, self.logger
        )
        self.recruitment_stage_module = RecruitmentStageModule(
            self.agent_config.dbname, self.logger
        )
        self.recruitment_instruction_module = RecruitmentInstructionModule(
            self.agent_config.dbname, self.logger
        )
        self.if_created = False
        self.recruitment: Recruitment = None
        self.recruitment_instruction: Optional[RecruitmentInstruction] = None

        # behaviours
        self.check_recruitments_behav: CheckRecruitments = None
        self.prepare_recruitment_behav: PrepareRecruitment = None
        self.agent_communication_behav: AgentCommunication = None

    async def setup(self):
        await super().setup()

        self.check_recruitments_behav = CheckRecruitments()
        self.agent_communication_behav = AgentCommunication()

        self.add_behaviour(self.check_recruitments_behav)
        self.add_behaviour(self.agent_communication_behav)


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
                "No recruitments found. Recruitment with job_offer_id: %s and candidate_id: %s to be created.",
                self.agent.job_offer_id,
                self.agent.candidate_id,
            )
        else:
            self.agent.if_created = True
            self.agent.recruitment = recruitments[0]

            self.agent.logger.info(
                "Found recruitment with id: %s. No recruitment objects will be created.",
                recruitments[0]._id,
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

        if self.agent.recruitment_instruction is None:
            self.agent.logger.error("Exiting agent - no recruitment instruction found.")
            await self.agent.stop()

    async def create_recruitment(self):
        if self.agent.if_created:
            return

        self.agent.recruitment = Recruitment(
            "", self.agent.job_offer_id, self.agent.candidate_id, 1, False, 0.0
        )

        id = self.agent.recruitment_module.create(self.agent.recruitment)
        self.agent.recruitment._id = id

    async def create_stage_agents(self):
        for i in range(len(self.agent.recruitment_instruction.stage_priorities)):
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
                "%d) Started RSM agent for recruitment with id: %s.",
                i,
                self.agent.recruitment._id,
            )


class AgentCommunication(spade.behaviour.CyclicBehaviour):
    """Behaviour representing ManageStageRequest, ManageStageResponse, ReceiveStageResult and ReceiveApplicationRating protocols"""

    agent: RecruitmentManagerAgent

    def __init__(self):
        super().__init__()

        self.dispatcher = {
            MessageType.START_REQUEST: self.handle_start_request,
            MessageType.STAGE_RESULT: self.handle_stage_result,
            MessageType.ANALYSIS_RESULT: self.handle_analysis_result,
        }

    async def run(self):
        self.agent.logger.info("AgentCommunication behaviour run.")

        await self.receive_and_dispatch()

    async def receive_and_dispatch(self):
        msg = await self.receive(timeout=30)
        if msg is None:
            await self.check_current_priority()
            return

        type, data = await self.agent.get_message_type_and_data(msg)

        handler = self.dispatcher.get(type, self.handle_unknown_message)
        await handler(data)

    async def handle_start_request(self, data: List[str]):
        self.agent.logger.info(
            "Received message with start request from rsm agent with jid: %s", data[0]
        )

        start_permission = await self.validate_priority(int(data[1]))
        msg = await self.agent.prepare_message(
            data[0],
            "response",
            "start_permission",
            MessageType.START_RESPONSE,
            [f"{start_permission}"],
        )

        self.agent.logger.info(
            "Sending message to rsm agent with the start permission."
        )
        await self.send(msg)

    async def handle_stage_result(self, data: List[str]):
        self.agent.logger.info(
            "Received message with stage result from rsm agent with jid: %s", data[0]
        )

        await self.update_overall_result(float(data[1]))
        await self.should_update_priority()

        msg = await self.agent.prepare_message(
            data[0],
            "response",
            "ack",
            MessageType.STAGE_RESULT_ACK,
            ["ACK"],
        )
        self.agent.logger.info(
            "Sending message to rsm agent to acknowledge the receipt of stage result."
        )
        await self.send(msg)

    async def update_overall_result(self, stage_result: float):
        self.agent.recruitment.overall_result += stage_result
        self.agent.recruitment_module.increment(
            self.agent.recruitment._id,
            {"overall_result": stage_result},
        )

    async def should_update_priority(self):
        recruitment_stages = (
            self.agent.recruitment_stage_module.get_by_recruitment_and_priority(
                self.agent.recruitment._id, self.agent.recruitment.current_priority
            )
        )
        should_change = all(
            rs.status == RecruitmentStageStatus.DONE for rs in recruitment_stages
        )

        if should_change:
            self.agent.logger.info(
                "Updating current priority to: %d.",
                self.agent.recruitment.current_priority + 1,
            )

            self.agent.recruitment.current_priority += 1
            self.agent.recruitment_module.increment(
                self.agent.recruitment._id,
                {"current_priority": 1},
            )

    async def check_current_priority(self):
        should_end = self.agent.recruitment.current_priority > max(
            self.agent.recruitment_instruction.stage_priorities
        )

        if should_end:
            self.agent.logger.info(
                "All recruitment stages are DONE. Ending AgentCommunication behaviour..."
            )

            recruitments = self.agent.recruitment_module.get_by_job_and_candidate(
                self.agent.job_offer_id, self.agent.candidate_id
            )
            if len(recruitments) == 0:
                f"No recruitments with job_offer_id: {self.agent.job_offer_id} and candidate_id: {self.agent.candidate_id} found."
                self.kill()
                return

            _ = self.agent.jobOffer_module.change_application_status(
                self.agent.job_offer_id,
                [self.agent.candidate_id],
                ApplicationStatus.FINISHED,
            )

            if recruitments[0].notif_sent == True:
                self.kill()
                return

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
                MessageType.NOTIF_CANDIDATE_CAN_REQUEST,
                [
                    f"{recruitments[0].candidate_id}",
                    "Congratulations on completing all stages of recruitment. we will get back to you soon",
                ],
            )

            await self.send(msg)
            self.agent.recruitment_module.update(
                recruitments[0]._id,
                {"notif_sent": True},
            )
            self.agent.logger.info(
                "Sent message to notification agent with the notif request."
            )
            self.kill()
            return

    async def handle_analysis_result(self, data: List[str]):
        self.agent.logger.info(
            "Received message with CV analysis result equal to %s", data[0]
        )

        recruitments = self.agent.recruitment_module.get_by_job_and_candidate(
            self.agent.job_offer_id,
            self.agent.candidate_id,
        )
        if len(recruitments) == 0:
            self.agent.logger.info(
                "No recruitments with job_offer_id: %s and candidate_id: %s found.",
                self.agent.job_offer_id,
                self.agent.candidate_id,
            )
            return

        result = self.agent.recruitment_module.update(
            recruitments[0]._id, {"application_rating": int(data[0])}
        )
        if result:
            self.agent.logger.info(
                "Successfully saved the candidate %s rating for job offer %s",
                self.agent.candidate_id,
                self.agent.job_offer_id,
            )
        else:
            self.agent.logger.info(
                "Failed to save the candidate %s rating for job offer %s",
                self.agent.candidate_id,
                self.agent.job_offer_id,
            )

    async def handle_unknown_message(self):
        self.agent.logger.warning("Unknown message type received, ignoring...")

    async def validate_priority(self, stage_priority: int) -> bool:
        return self.agent.recruitment.current_priority == stage_priority
