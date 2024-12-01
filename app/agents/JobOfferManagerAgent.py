import spade.behaviour

from app.agents.RecruitmentManagerAgent import RecruitmentManagerAgent
from app.dataaccess.model.CandidateProfile import CandidateProfile
from app.dataaccess.model.JobOffer import ApplicationDetails, ApplicationStatus
from app.modules.CandidateModule import CandidateModule
from app.modules.JobOfferModule import JobOfferModule

from .base.BaseAgent import BaseAgent

AWAIT_APPLICATION_PERIOD = 5


class JobOfferManagerAgent(BaseAgent):
    def __init__(self, job_offer_id):
        super().__init__(job_offer_id)
        self.jobOfferModule = JobOfferModule(self.agent_config.dbname, self.logger)
        self.candidateModule = CandidateModule(self.agent_config.dbname, self.logger)
        self.job_offer_id = job_offer_id
        self.jobOffer = None
        self.applications_to_init: list[ApplicationDetails] = None
        self.recruitments: dict[str, RecruitmentManagerAgent] = {}
        self.candidates_to_process: list[ApplicationDetails] = None

        # behaviours
        self.processCandidateBehav: ProcessCandidate = None
        self.initRmentsBehav: InitRecruitments = None
        self.awaitApplicationBehav: AwaitApplication = None

    async def setup(self):
        await super().setup()

        self.jobOffer = self.jobOfferModule.get(self.job_offer_id)
        if self.jobOffer is None:
            self.logger.error("Job offer not found.")
            await self.stop()

        self.applications_to_init = [x for x in self.jobOffer.applications
                                     if x.status != ApplicationStatus.NEW]

        self.initRmentsBehav = InitRecruitments()
        self.add_behaviour(self.initRmentsBehav)
        self.awaitApplicationBehav = AwaitApplication(period=AWAIT_APPLICATION_PERIOD)
        self.add_behaviour(self.awaitApplicationBehav)


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
                self.agent.logger.info("Starting RmentAgent for job '%s', candidate '%s'",
                                       self.agent.jobOffer.id, app.candidate_id)
                rment_agent = RecruitmentManagerAgent(self.agent.jobOffer.id, app.candidate_id)
                self.agent.recruitments[app.candidate_id] = rment_agent
                await rment_agent.start()
            else:
                self.agent.logger.info("Skipping %s, agent already exists.", app.candidate_id)


class AwaitApplication(spade.behaviour.PeriodicBehaviour):
    """
    Awaits new applications for job offer and triggers processing.
    Protocols/Activities in GAIA (role ApplicationHandler): AwaitApplication, ProcessApplication
    """

    agent: JobOfferManagerAgent

    async def run(self):
        self.agent.logger.info("AwaitApplication behaviour run.")
        new_applications = self.check_new_applications()
        if len(new_applications) > 0:
            await self.process_candidates(new_applications)

    def check_new_applications(self) -> list[ApplicationDetails]:
        new_applications = self.agent.jobOfferModule.get_new_applications(self.agent.job_offer_id)

        # ProcessApplication activity
        result = self.agent.jobOfferModule.change_application_status(
            self.agent.job_offer_id,
            [x.candidate_id for x in new_applications],
            ApplicationStatus.PROCESSED
        )

        return new_applications if result else []

    async def process_candidates(self, new_applications: list[ApplicationDetails]):
        self.agent.candidates_to_process = new_applications
        self.agent.processCandidateBehav = ProcessCandidate()
        self.agent.add_behaviour(self.agent.processCandidateBehav)
        await self.agent.processCandidateBehav.join()


class ProcessCandidate(spade.behaviour.OneShotBehaviour):
    """
    ProcessCandidate activity in role JOM
    """

    agent: JobOfferManagerAgent

    async def run(self):
        self.agent.logger.info("ProcessCandidate behaviour run.")
        applications = self.agent.candidates_to_process
        self.agent.candidates_to_process = None

        candidate_profiles = [CandidateProfile(appl.candidate_id, appl.name, appl.surname,
                                               appl.email, [self.agent.job_offer_id])
                              for appl in applications]

        for cand in candidate_profiles:
            self.agent.candidateModule.try_add_candidate(cand)

        await self.init_recr(applications)

    async def init_recr(self, new_applications: list[ApplicationDetails]):
        self.agent.applications_to_init = new_applications
        if len(self.agent.applications_to_init) > 0:
            self.agent.initRmentsBehav = InitRecruitments()
            self.agent.add_behaviour(self.agent.initRmentsBehav)
            await self.agent.initRmentsBehav.join()
