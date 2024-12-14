import asyncio
import random
import spade.behaviour

from app.agents.RecruitmentManagerAgent import RecruitmentManagerAgent
from app.dataaccess.model.JobOffer import ApplicationStatus
from app.dataaccess.model.MessageType import MessageType
from app.modules.JobOfferModule import JobOfferModule
from app.utils.configuration import MASConfiguration

from .base.BaseAgent import BaseAgent


class ApplicationAnalyzerAgent(BaseAgent):
    _instances: int = 0

    def __init__(
        self,
    ):
        ApplicationAnalyzerAgent._instances = ApplicationAnalyzerAgent._instances + 1
        super().__init__(f"{ApplicationAnalyzerAgent._instances}")

        self.rmentJID = self.config.agents[RecruitmentManagerAgent.__name__.split('.')[-1]].jid

        self.jobOfferModule = JobOfferModule(self.agent_config.dbname, self.logger)

        # behaviours
        self.analyzeBehav: Analyze = None

    async def setup(self):
        await super().setup()

        self.analyzeBehav = Analyze()
        self.add_behaviour(self.analyzeBehav)


class Analyze(spade.behaviour.CyclicBehaviour):
    """
    Awaits application analyze request, performs analysis and sends rate.
    Protocols/Activities in GAIA (role ApplicationAnalyzer): AnalyzeRequest, RateCandidate, AnalyzeResponse
    """

    agent: ApplicationAnalyzerAgent

    async def run(self):
        self.agent.logger.info("Waiting for application analisis request.")

        # AnalyzeRequest protocol
        msg = await self.receive(timeout=120)
        if msg is None:
            return
        
        self.agent.logger.info("Received analyze request: %s", msg.body)

        _, data = await self.agent.get_message_type_and_data(msg)

        result = self.agent.jobOfferModule.change_application_status(
            data[0],
            [data[1]],
            ApplicationStatus.IN_ANALYSIS,
        )

        if result is None:
            return
        
        # RateCandidate activity
        await asyncio.sleep(10)
        
        analysis_result = random.randint(0, 100)

        result = self.agent.jobOfferModule.change_application_status(
            data[0],
            [data[1]],
            ApplicationStatus.ANALYZED,
        )

        if result is None:
            return
        
        # AnalyzeResponse protocol
        msg = await self.agent.prepare_message(
            f"{self.agent.rmentJID}_{data[0]}_{data[1]}@{self.agent.config.server.name}", 
            "response", 
            "analyze", 
            MessageType.ANALYSIS_RESULT,
            [f"{analysis_result}"]
        )

        await self.send(msg)

        self.agent.logger.info("Sent message to rm agent with the CV analysis result.")