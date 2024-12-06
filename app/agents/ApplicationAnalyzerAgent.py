import spade.behaviour

from app.dataaccess.model.RecruitmentStage import RecruitmentStage
from app.modules.RecruitmentStageModule import RecruitmentStageModule

from .base.BaseAgent import BaseAgent


class ApplicationAnalyzerAgent(BaseAgent):
    def __init__(
        self,
    ):
        super().__init__("analyzer")

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
        self.agent.logger.info("Analyze behaviour run.")

        msg = await self.receive(timeout=10) # TODO: is timeout needed?
        if msg:
            self.agent.logger.info("Received message: %s", msg.body)
        else:
            self.agent.logger.info(
                "No message received within the timeout."
            )