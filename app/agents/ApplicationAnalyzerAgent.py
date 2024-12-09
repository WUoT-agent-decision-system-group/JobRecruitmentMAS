import spade.behaviour

from app.dataaccess.model.JobOffer import ApplicationStatus
from app.modules.JobOfferModule import JobOfferModule

from .base.BaseAgent import BaseAgent


class ApplicationAnalyzerAgent(BaseAgent):
    _instances: int = 0

    def __init__(
        self,
    ):
        ApplicationAnalyzerAgent._instances = ApplicationAnalyzerAgent._instances + 1
        super().__init__(f"{ApplicationAnalyzerAgent._instances}")

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
        self.agent.logger.info("Analyze behaviour run.")

        msg = await self.receive(timeout=10) # TODO: is timeout needed?
        if msg:
            self.agent.logger.info("Received message: %s", msg.body)

            body = msg.body.split("%")

            # ProcessApplication activity
            result = self.agent.jobOfferModule.change_application_status(
                body[0],
                [body[1]],
                ApplicationStatus.IN_ANALYSIS,
            )
        else:
            self.agent.logger.info(
                "No message received within the timeout."
            )