import random
import spade.behaviour

from app.agents.RecruitmentManagerAgent import RecruitmentManagerAgent
from app.dataaccess.model.JobOffer import ApplicationStatus
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

        self.rmentJID = self.config.agents[RecruitmentManagerAgent.__class__.__name__].jid

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

        # AnalyzeRequest protocol
        msg = await self.receive(timeout=10) # TODO: is timeout needed?
        if msg:
            self.agent.logger.info("Received analyze request: %s", msg.body)

            body = msg.body.split("%")

            result = self.agent.jobOfferModule.change_application_status(
                body[0],
                [body[1]],
                ApplicationStatus.IN_ANALYSIS,
            )

            if result:
                # RateCandidate activity
                analysis_result = random.randint(0, 100)

                result = self.agent.jobOfferModule.change_application_status(
                    body[0],
                    [body[1]],
                    ApplicationStatus.ANALYZED,
                )

                if result:
                    # AnalyzeResponse protocol
                    msg = await self.agent.prepare_message(
                        f"{self.rmentJID}_{body[0]}_{body[1]}@{self.config.server.name}", 
                        ["response"], 
                        ["analyze"], 
                        f"{analysis_result}"
                    )

                    await self.send(msg)
            
                    self.agent.logger.info("Sent message to rm agent with the CV analysis result.")

        else:
            self.agent.logger.info(
                "No message received within the timeout."
            )