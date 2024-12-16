import random

import spade.behaviour

from app.agents import ApplicationAnalyzerAgent, NotificationAgent
from app.agents.RecruitmentManagerAgent import RecruitmentManagerAgent
from app.dataaccess.model.CandidateProfile import CandidateProfile
from app.dataaccess.model.JobOffer import (
    ApplicationDetails,
    ApplicationStatus,
    JobOfferStatus,
)
from app.dataaccess.model.MessageType import MessageType
from app.modules.CandidateModule import CandidateModule
from app.modules.JobOfferModule import JobOfferModule
from app.modules.RecruitmentModule import RecruitmentModule

from .base.BaseAgent import BaseAgent

AWAIT_APPLICATION_PERIOD = 15
AWAIT_APPLICATION_FINISHED_PERIOD = 30


class JobOfferManagerAgent(BaseAgent):
    def __init__(self, job_offer_id: str):
        super().__init__(job_offer_id)
        self.jobOfferModule = JobOfferModule(self.agent_config.dbname, self.logger)
        self.candidateModule = CandidateModule(self.agent_config.dbname, self.logger)
        self.recruitmentModule = RecruitmentModule(
            self.agent_config.dbname, self.logger
        )
        self.job_offer_id = job_offer_id
        self.jobOffer = None
        self.applications_to_init: list[ApplicationDetails] = None
        self.recruitments: dict[str, RecruitmentManagerAgent] = {}
        self.candidates_to_process: list[ApplicationDetails] = None
        self.applications_to_analyze: list[ApplicationDetails] = None

        # behaviours
        self.processCandidateBehav: ProcessCandidate = None
        self.triggerAnalysisBehav: TriggerAnalysis = None
        self.initRmentsBehav: InitRecruitments = None
        self.awaitApplicationBehav: AwaitApplication = None
        self.getStatusResponse: GetStatusResponse = None
        self.finishedRecruitmentRequest: GetStatusResponse = None

    async def setup(self):
        await super().setup()

        self.jobOffer = self.jobOfferModule.get(self.job_offer_id)
        if self.jobOffer is None:
            self.logger.error("Job offer not found.")
            await self.stop()

        self.applications_to_init = [
            x
            for x in self.jobOffer.applications
            if (
                x.status != ApplicationStatus.NEW
                and x.status != ApplicationStatus.REJECTED
            )
        ]

        self.initRmentsBehav = InitRecruitments()
        self.add_behaviour(self.initRmentsBehav)
        self.awaitApplicationBehav = AwaitApplication(period=AWAIT_APPLICATION_PERIOD)
        self.add_behaviour(self.awaitApplicationBehav)
        self.getStatusResponse = GetStatusResponse()
        self.add_behaviour(self.getStatusResponse)
        self.finishedRecruitmentRequest = FinishedRecruitmentRequest(
            period=AWAIT_APPLICATION_FINISHED_PERIOD
        )
        self.add_behaviour(self.finishedRecruitmentRequest)


class InitRecruitments(spade.behaviour.OneShotBehaviour):
    """
    Initiates RmentAgents for applications in `self.agent.applications_to_init`.
    """

    agent: JobOfferManagerAgent

    async def run(self):
        self.agent.logger.info("InitRecruitments behaviour run.")
        apps = self.agent.applications_to_init
        if apps is None:
            return
        self.agent.applications_to_init = None
        for app in apps:
            if app.candidate_id not in self.agent.recruitments:
                self.agent.logger.info(
                    "Starting RmentAgent for job '%s', candidate '%s'",
                    self.agent.jobOffer.id,
                    app.candidate_id,
                )
                rment_agent = RecruitmentManagerAgent(
                    self.agent.jobOffer.id, app.candidate_id
                )
                self.agent.recruitments[app.candidate_id] = rment_agent
                await rment_agent.start()
            else:
                self.agent.logger.info(
                    "Skipping %s, agent already exists.", app.candidate_id
                )


class AwaitApplication(spade.behaviour.PeriodicBehaviour):
    """
    Awaits new applications for job offer and triggers processing.
    Protocols/Activities in GAIA (role ApplicationHandler): AwaitApplication, ProcessApplication
    """

    agent: JobOfferManagerAgent

    async def run(self):
        if self.agent.jobOffer.status != JobOfferStatus.CLOSED:
            self.agent.logger.info("AwaitApplication behaviour run.")
            applications_to_process = self.check_applications_to_process()
            if len(applications_to_process) > 0:
                await self.process_candidates(applications_to_process)
                await self.trigger_analysis(applications_to_process)
        self.agent.jobOffer = self.agent.jobOfferModule.get(self.agent.job_offer_id)

    def check_applications_to_process(self) -> list[ApplicationDetails]:
        new_applications = self.agent.jobOfferModule.get_new_applications(
            self.agent.job_offer_id
        )

        applications_to_process = []
        applications_to_reject = []
        old_applications = len(self.agent.jobOffer.applications)

        for app in new_applications:
            if old_applications + 1 <= self.agent.jobOffer.max_number_of_candidates:
                applications_to_process.append(app)
                old_applications = old_applications + 1
            else:
                applications_to_reject.append(app)

        result = self.agent.jobOfferModule.change_application_status(
            self.agent.job_offer_id,
            [x.candidate_id for x in applications_to_process],
            ApplicationStatus.PROCESSED,
        )

        _ = self.agent.jobOfferModule.change_application_status(
            self.agent.job_offer_id,
            [x.candidate_id for x in applications_to_reject],
            ApplicationStatus.REJECTED,
        )

        if len(applications_to_process) > 0:
            self.agent.jobOfferModule.change_job_offer_status(
                self.agent.job_offer_id, JobOfferStatus.INPROGRESS
            )

        return applications_to_process if result else []

    async def process_candidates(self, new_applications: list[ApplicationDetails]):

        self.agent.candidates_to_process = new_applications
        self.agent.processCandidateBehav = ProcessCandidate()
        self.agent.add_behaviour(self.agent.processCandidateBehav)
        await self.agent.processCandidateBehav.join()

    async def trigger_analysis(self, processed_applications: list[ApplicationDetails]):
        self.agent.applications_to_analyze = processed_applications
        self.agent.triggerAnalysisBehav = TriggerAnalysis()
        self.agent.add_behaviour(self.agent.triggerAnalysisBehav)
        await self.agent.triggerAnalysisBehav.join()


class ProcessCandidate(spade.behaviour.OneShotBehaviour):
    """
    ProcessCandidate activity in role JOM
    """

    agent: JobOfferManagerAgent

    async def run(self):
        self.agent.logger.info("ProcessCandidate behaviour run.")
        applications = self.agent.candidates_to_process
        self.agent.candidates_to_process = None

        candidate_profiles = [
            CandidateProfile(
                appl.candidate_id,
                appl.name,
                appl.surname,
                appl.email,
                [self.agent.job_offer_id],
            )
            for appl in applications
        ]

        for cand in candidate_profiles:
            self.agent.candidateModule.try_add_candidate(cand)

        await self.init_recr(applications)

    async def init_recr(self, new_applications: list[ApplicationDetails]):
        self.agent.applications_to_init = new_applications
        if len(self.agent.applications_to_init) > 0:
            self.agent.initRmentsBehav = InitRecruitments()
            self.agent.add_behaviour(self.agent.initRmentsBehav)
            await self.agent.initRmentsBehav.join()


class TriggerAnalysis(spade.behaviour.OneShotBehaviour):
    """
    Sends analyze request to ApplicationAnalyzer
    Protocols/Activities in GAIA (role ApplicationHandler): TriggerAnalysis
    """

    agent: JobOfferManagerAgent

    async def run(self):
        self.agent.logger.info("TriggerAnalysis behaviour run.")

        to_analyze = self.agent.applications_to_analyze
        analyzerJID = self.agent.config.agents[
            ApplicationAnalyzerAgent.__name__.split(".")[-1]
        ].jid
        analyzers_count = self.agent.config.agents[
            ApplicationAnalyzerAgent.__name__.split(".")[-1]
        ].defined_instances
        for app in to_analyze:
            msg = await self.agent.prepare_message(
                f"{analyzerJID}_{random.randint(1, analyzers_count)}@{self.agent.config.server.name}",
                "request",
                "analyze",
                MessageType.ANALYSIS_REQUEST,
                [self.agent.job_offer_id, app.candidate_id],
            )

            await self.send(msg)

        self.agent.logger.info(
            "Sent message(s) to analyzer agent with the request to analyze CV."
        )

        self.agent.applications_to_analyze = None


class GetStatusResponse(spade.behaviour.CyclicBehaviour):
    """
    Sends analyze request to RecruiterManager
    Protocols/Activities in GAIA (role JobOfferManager): GetStatusRequest, GetStatusResponse
    """

    agent: JobOfferManagerAgent

    async def run(self):
        msg = await self.receive(timeout=120)
        if msg is None:
            return

        self.agent.logger.info("Received get status request from %s.", msg.sender)
        type, _ = await self.agent.get_message_type_and_data(msg)

        if type != MessageType.STATUS_REQUEST:
            self.agent.logger.warning("Received an unknown or invalid message.")
            return

        jobOffer = self.agent.jobOffer
        if jobOffer is None:
            self.agent.logger.error("Job offer not found.")
            await self.agent.stop()

        finished_applications = [
            x for x in jobOffer.applications if x.status == ApplicationStatus.FINISHED
        ]
        analysed_applications = [
            x for x in jobOffer.applications if x.status == ApplicationStatus.ANALYZED
        ]
        rejected_applications = [
            x for x in jobOffer.applications if x.status == ApplicationStatus.REJECTED
        ]

        msg = await self.agent.prepare_message(
            f"{msg.sender}",
            "response",
            "status",
            MessageType.STATUS_RESPONSE,
            [
                f"{jobOffer._id}",
                f"{jobOffer.name}",
                f"{jobOffer.status.value}",
                f"{jobOffer.description}",
                f"{len(finished_applications)}",
                f"{len(analysed_applications)}",
                f"{len(rejected_applications)}",
                f"{jobOffer.best_candidate_id}",
            ],
        )

        await self.send(msg)

        self.agent.logger.info("Sent message status result to %s.", msg.sender)


class FinishedRecruitmentRequest(spade.behaviour.PeriodicBehaviour):
    """
    Sends analyze request to RecruiterManager
    Protocols/Activities in GAIA (role JobOfferManager): FinishedRecruitmentRequest, UpdateCandidatesRanking, CandidatesResult,
    ChooseBestCandidates, InformRecruiter, QueueResultNotification, Close
    """

    agent: JobOfferManagerAgent

    async def run(self):
        finished_applications = self.agent.jobOfferModule.get_finished_applications(
            self.agent.job_offer_id
        )

        if (
            len(finished_applications) == self.agent.jobOffer.max_number_of_candidates
            and self.agent.jobOffer.status != JobOfferStatus.CLOSED
        ):
            self.agent.logger.info("Closing job offer")
            self.agent.jobOfferModule.change_job_offer_status(
                self.agent.job_offer_id, JobOfferStatus.CLOSED
            )
            await self.chooseBestCandidate(finished_applications)
            await self.sendNotifToAllCandidates()

    async def chooseBestCandidate(
        self, finished_applications: list[ApplicationDetails]
    ):
        bestResult = 0
        bestCandidate = None
        for app in finished_applications:
            recruitments = self.agent.recruitmentModule.get_by_job_and_candidate(
                self.agent.job_offer_id, app.candidate_id
            )
            if len(recruitments) == 0:
                self.agent.logger.info(
                    "No recruitments found. Recruitment with job_offer_id: %s and candidate_id: %s to be created.",
                    self.agent.job_offer_id,
                    self.agent.candidate_id,
                )
            candidateResult = (
                recruitments[0].application_rating + recruitments[0].overall_result
            )
            if candidateResult > bestResult:
                bestCandidate = app.candidate_id
                bestResult = candidateResult
        self.agent.jobOfferModule.update(
            self.agent.job_offer_id, {"best_candidate_id": bestCandidate}
        )

    async def sendNotifToAllCandidates(self):
        jobOffer = self.agent.jobOfferModule.get(self.agent.job_offer_id)

        prefix = self.agent.config.agents[NotificationAgent.__name__.split(".")[-1]].jid
        instances = self.agent.config.agents[
            NotificationAgent.__name__.split(".")[-1]
        ].defined_instances

        message = ""
        for app in jobOffer.applications:
            if app.status == ApplicationStatus.FINISHED:
                if app.candidate_id == jobOffer.best_candidate_id:
                    message = "Congratulations!!! You were the best candidate in the recruitment process."
                else:
                    message = "Sorry. Unfortunately, there were better candidates for this position."

            else:
                message = "Unfortunately, too many applications, it was decided not to consider your candidacy."

            msg = await self.agent.prepare_message(
                f"{prefix}_{random.randint(1, instances)}@{self.agent.config.server.name}",
                "request",
                "notif",
                (
                    MessageType.NOTIF_CANDIDATE_CAN_REQUEST
                    if app.status == ApplicationStatus.FINISHED
                    else MessageType.NOTIF_CANDIDATE_REJECTED_REQUEST
                ),
                [
                    f"{app.candidate_id if app.status == ApplicationStatus.FINISHED else app.email}",
                    message,
                ],
            )

            await self.send(msg)
            self.agent.logger.info(
                "Sent message to notification agent with the notif request for %s.",
                app.candidate_id,
            )
