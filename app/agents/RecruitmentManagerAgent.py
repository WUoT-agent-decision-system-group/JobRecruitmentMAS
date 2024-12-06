from typing import Type

import spade.behaviour

from app.dataaccess.model.Recruitment import Recruitment
from app.dataaccess.model.RecruitmentInstruction import RecruitmentInstruction
from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.modules.RecruitmentInstructionModule import RecruitmentInstructionModule
from app.modules.RecruitmentModule import RecruitmentModule
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent
from .RecruitmentStageManagerAgent import RecruitmentStageManagerAgent

STAGES_NUMBER = 2


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
        self.recruitment: Recruitment = None
        self.recruitment_instruction: RecruitmentInstruction = None

        # behaviours
        self.prepare_recruitment_behav: PrepareRecruitment = None
        self.stage_communication_behav: StageCommunication = None

    async def setup(self):
        await super().setup()

        self.prepare_recruitment_behav = PrepareRecruitment()
        self.stage_communication_behav = StageCommunication()

        self.add_behaviour(self.prepare_recruitment_behav)
        self.add_behaviour(self.stage_communication_behav)


class PrepareRecruitment(spade.behaviour.OneShotBehaviour):
    """Creates recruitment object (if not present) and initiates RmentStageAgents (one per one stage)"""

    agent: RecruitmentManagerAgent

    async def run(self):
        self.agent.logger.info("PrepareRecruitment behaviour run.")

        await self.create_recruitment()
        await self.get_recruitment_instruction()
        await self.create_stage_agents()

    async def create_recruitment(self):
        self.agent.recruitment = Recruitment(
            "", self.agent.job_offer_id, self.agent.candidate_id
        )

        id = self.agent.recruitment_module.create(self.agent.recruitment)
        self.agent.recruitment._id = id

    async def get_recruitment_instruction(self):
        self.agent.recruitment_instruction = (
            self.agent.recruitment_instruction_module.get_by_job_offer_id(
                self.agent.job_offer_id
            )
        )

    async def create_stage_agents(self):
        for i in range(self.agent.recruitment_instruction.stages_number):
            recruitment_stage_attr = {
                "status": 1,
                "type": self.agent.recruitment_instruction.stage_types[i].value,
                "priority": self.agent.recruitment_instruction.stage_priorities[i],
            }
            rment_stage_agent = RecruitmentStageManagerAgent(
                self.agent.recruitment._id, i, recruitment_stage_attr
            )

            await rment_stage_agent.start()

            self.agent.logger.info(
                f"{i}) Started RSM agent for recruitment with id: {self.agent.recruitment._id}."
            )


class StageCommunication(spade.behaviour.CyclicBehaviour):
    async def run(self):
        pass
