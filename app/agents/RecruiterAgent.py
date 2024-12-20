import spade

from app.agents import JobOfferManagerAgent
from app.dataaccess.model import JobOffer, Recruiter
from app.dataaccess.model.MessageType import MessageType
from app.modules.RecruiterModule import RecruiterModule

from .base.BaseAgent import BaseAgent

GET_STATUS_PERIOD = 20


class RecruiterAgent(BaseAgent):
    def __init__(self, recruiter_id: str, offers_id: list[str]):
        super().__init__(recruiter_id)
        self.recruiter: Recruiter = None
        self.offers_id = offers_id
        self.recruiter_id = recruiter_id
        self.recruiterModule = RecruiterModule(self.agent_config.dbname, self.logger)

        # behaviours
        self.get_job_offers_stats_behav: GetStatus = None
        self.create_analysis_behav: CreateAnalysis = None

    async def setup(self):
        await super().setup()
        self.recruiter = self.recruiterModule.get(self.recruiter_id)
        if self.recruiter is None:
            self.logger.error("Recruiter information not found.")
            await self.stop()

        self.logger.info(
            "Hello! I am representant of %s, %s.",
            self.recruiter.name,
            self.recruiter.surname,
        )
        self.get_job_offers_stats_behav = GetStatus(period=GET_STATUS_PERIOD)
        self.add_behaviour(self.get_job_offers_stats_behav)


class GetStatus(spade.behaviour.PeriodicBehaviour):
    """
    Request to job managers to send information of the current job offers status.
    Activities in GAIA (role RecruiterManager): GetStatus
    """

    agent: RecruiterAgent

    async def run(self):
        if not self.agent.create_analysis_behav:
            self.agent.logger.info("GetStatus behaviour run.")
            for offer_id in self.agent.offers_id:
                prefix = self.agent.config.agents[
                    JobOfferManagerAgent.__name__.split(".")[-1]
                ].jid
                self.agent.logger.info("Try to send to %s_%s", prefix, offer_id)
                msg = await self.agent.prepare_message(
                    f"{prefix}_{offer_id}@{self.agent.config.server.name}",
                    "request",
                    "status",
                    MessageType.STATUS_REQUEST,
                    [],
                )
                await self.send(msg)
                self.agent.logger.info(
                    "A message has been sent to %s_%s", prefix, offer_id
                )
            self.agent.logger.info(
                "A message has been sent to job agents requesting status."
            )

            self.agent.create_analysis_behav = CreateAnalysis()
            self.agent.add_behaviour(self.agent.create_analysis_behav)
            await self.agent.create_analysis_behav.join()
            self.agent.logger.info("Analysis created.")
            self.agent.create_analysis_behav = None


class CreateAnalysis(spade.behaviour.OneShotBehaviour):
    """
    Behaviour that waits for responses from all job offer agents, collects the data,
    and performs analysis once all responses are received or timeout is reached for some.
    """

    agent: RecruiterAgent

    async def on_start(self):
        self.expected_offers = set(self.agent.offers_id)
        self.responses = {}
        self.agent.logger.info(
            "Expecting responses from job offer managers: %s", self.expected_offers
        )

    async def run(self):
        self.agent.logger.info("Waiting for job offer status responses...")
        for _ in self.expected_offers:
            msg = await self.receive(
                timeout=GET_STATUS_PERIOD / (len(self.expected_offers) + 1)
            )

            if msg:
                self.agent.logger.info("Received message from %s", msg.sender)
                type, data = await self.agent.get_message_type_and_data(msg)

                if type == MessageType.STATUS_RESPONSE:
                    self.responses[data[0]] = [
                        data[1],
                        data[2],
                        data[3],
                        data[4],
                        data[5],
                        data[6],
                        data[7],
                    ]
                else:
                    self.agent.logger.warning(
                        "Received an unknown or invalid message for offer %s.", data[0]
                    )
            else:
                self.agent.logger.warning("Timeout reached.")

        if set(self.responses.keys()) == self.expected_offers:
            self.agent.logger.info("All responses received. Proceeding with analysis.")
            self.perform_analysis()
        else:
            missing_offers = self.expected_offers - set(self.responses.keys())
            self.agent.logger.warning(
                "Analysis incomplete. Missing responses for: %s.", missing_offers
            )

    def perform_analysis(self):
        """
        Perform detailed analysis of job offer statuses and applications.
        """
        self.agent.logger.info("Performing detailed analysis on job offer statuses...")

        for offer_id, data in self.responses.items():
            name = data[0]
            status = data[1]
            description = data[2]
            finished_applications = data[3]
            analysed_applications = data[4]
            rejected_applications = data[5]
            best_candidate_id = data[6]

            offer_analysis = (
                f"Job Offer: {name} (ID: {offer_id})\n"
                f"Description: {description}\n"
                f"Status: { JobOffer.JobOfferStatus(int(status))}\n"
                f"Finished Applications: {int(finished_applications)}\n"
                f"Applications in progress: {int(analysed_applications)}\n"
                f"Rejected Applications: {int(rejected_applications)}\n"
                f"Bestcandidate: (ID: {best_candidate_id})"
            )

            self.agent.logger.info("Detailed Analysis Report:\n%s", offer_analysis)
