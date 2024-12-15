import spade

from app.dataaccess.model.MessageType import MessageType
from app.modules.CandidateModule import CandidateModule
from app.modules.RecruitmentModule import RecruitmentModule
from .base.BaseAgent import BaseAgent

class NotificationAgent(BaseAgent):
    def __init__(self, index: int):
        super().__init__(f"{index}")
        self.candidateModule = CandidateModule(self.agent_config.dbname, self.logger)
        self.recruitmentModule = RecruitmentModule(self.agent_config.dbname, self.logger)
        
        # behaviours
        self.processNotificationBehav: ProcessNotification = None

    async def setup(self):
        await super().setup()
        self.logger.info("Add behavior.")
        self.processNotificationBehav = ProcessNotification()
        self.add_behaviour(self.processNotificationBehav)




class ProcessNotification(spade.behaviour.CyclicBehaviour):
    """
    Process notification from other agents and simulate sending.
    Activities in GAIA (role NotificationHandler): SendNotificationRequest, SendNotificationResponse, ProcessNotification
    """

    agent: NotificationAgent

    async def run(self):
        self.agent.logger.info("Waiting for notification to send...")

        msg = await self.receive(timeout=30)  

        if msg:
            self.agent.logger.info("Received notification request from %s", msg.sender)
            type, data = await self.agent.get_message_type_and_data(msg)

            if type == MessageType.NOTIF_CANDIDATE_CAN_REQUEST:
                candidate = self.agent.candidateModule.get(data[0])
                self.agent.logger.info("Sending to %s message: %s", candidate.email, data[1])
            elif type == MessageType.NOTIF_CANDIDATE_RMENT_REQUEST:
                recruitment = self.agent.recruitmentModule.get(data[0])
                candidate = self.agent.candidateModule.get(recruitment.candidate_id)
                self.agent.logger.info("Sending to %s message: %s", candidate.email, data[1])
            else:
                self.agent.logger.warning("Received an unknown or invalid message for offert %s.", data[0])