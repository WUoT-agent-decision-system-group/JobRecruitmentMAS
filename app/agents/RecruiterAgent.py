import spade
from app.agents import JobOfferManagerAgent
from app.dataaccess.model import JobOffer, Recruiter
from app.dataaccess.model.MessageType import MessageType
from app.modules.RecruiterModule import RecruiterModule
from .base.BaseAgent import BaseAgent

GET_STATUS_PERIOD = 20

class RecruiterAgent(BaseAgent):
    def __init__(self, recruiter_id: str, offerts_id: list[str]):
        super().__init__(recruiter_id)  
        self.recruiter : Recruiter = None
        self.offerts_id = offerts_id
        self.recruiter_id = recruiter_id
        self.recruiterModule = RecruiterModule(self.agent_config.dbname, self.logger)
        
        # behaviours
        self.get_job_offerts_stats_behav: GetStatus = None
        self.present_analysis_behav: PresentAnalysis = None

    async def setup(self):
        await super().setup()
        self.recruiter = self.recruiterModule.get(self.recruiter_id)
        if self.recruiter is None:
            self.logger.error("Recruiter information not found.")
            await self.stop()

        self.logger.info(f"Hello! I am representant of {self.recruiter.name}, {self.recruiter.surname}.")
        self.get_job_offerts_stats_behav = GetStatus(period=GET_STATUS_PERIOD) 
        self.add_behaviour(self.get_job_offerts_stats_behav)


class GetStatus(spade.behaviour.PeriodicBehaviour):
    """
    Request to job managers to send information of the current job offerts status.
    Activities in GAIA (role RecruiterManager): GetStatus
    """

    agent: RecruiterAgent

    async def run(self):
        if not self.agent.present_analysis_behav:
            self.agent.logger.info("GetStatus behaviour run.")
            self.agent.logger.info(f"{self.agent.offerts_id}")
            for offert_id in self.agent.offerts_id:
                self.agent.logger.info(f"{offert_id}")
                prefix = self.agent.config.agents[JobOfferManagerAgent.__name__.split('.')[-1]].jid
                self.agent.logger.info(f"try to send to {prefix}_{offert_id}")
                msg = await self.agent.prepare_message(
                    f"{prefix}_{offert_id}@{self.agent.config.server.name}",
                    "request",
                    "status",
                    MessageType.STATUS_REQUEST,
                    []
                )
                await self.send(msg)
                self.agent.logger.info(f"A message has been sent to {prefix}_{offert_id}.")
            self.agent.logger.info("A message has been sent to job agents requesting status.")
        
            self.agent.present_analysis_behav = PresentAnalysis()
            self.agent.add_behaviour(self.agent.present_analysis_behav)
            await self.agent.present_analysis_behav.join()
            self.agent.logger.info("Analysis presented.")
            self.agent.present_analysis_behav = None

class PresentAnalysis(spade.behaviour.OneShotBehaviour):
    """
    Behaviour that waits for responses from all job offer agents, collects the data, 
    and performs analysis once all responses are received or timeout is reached for some.
    """

    agent: RecruiterAgent

    async def on_start(self):
        self.expected_offerts = set(self.agent.offerts_id)
        self.responses = {} 
        self.agent.logger.info(f"Expecting responses from job offer managers: {self.expected_offerts}")

    async def run(self):
        self.agent.logger.info("Waiting for job offer status responses...")
        for _ in self.expected_offerts:
            msg = await self.receive(timeout=GET_STATUS_PERIOD / (len(self.expected_offerts)+1))  

            if msg:
                self.agent.logger.info(f"Received message from {msg.sender}: {msg.body}")
                type, data = await self.agent.get_message_type_and_data(msg)
                                
                if type == MessageType.STATUS_RESPONSE:
                    self.responses[data[0]] = [data[1], data[2], data[3], data[4] ]
                    self.agent.logger.info(f"Collected status for offert {data[0]}.")
                else:
                    self.agent.logger.warning(f"Received an unknown or invalid message for offert {data[0]}.")
            else:
                self.agent.logger.warning(f"Timeout reached for offert {data[0]}, no response received.")

        if set(self.responses.keys()) == self.expected_offerts:
            self.agent.logger.info("All responses received. Proceeding with analysis.")
            self.perform_analysis()
        else:
            missing_offerts = self.expected_offerts - set(self.responses.keys())
            self.agent.logger.warning(f"Analysis incomplete. Missing responses for: {missing_offerts}")

    def perform_analysis(self):
        """
        Perform detailed analysis of job offer statuses and applications.
        """
        self.agent.logger.info("Performing detailed analysis on job offer statuses...")

        for offert_id, data in self.responses.items():
            name = data[0] 
            status = data[1]
            description = data[2]
            applications = data[3]

            offer_analysis = f"Job Offer: {name} (ID: {offert_id})\n" \
                         f"Description: {description}\n" \
                         f"Status: { JobOffer.JobOfferStatus(int(status))}\n" \
                         f"Total Applications: {int(applications)}"
            
            self.agent.logger.info(f"Detailed Analysis Report:\n{offer_analysis}")