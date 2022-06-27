from utils.domain.jsonlookupdomain import JSONLookupDomain
from services.nlu import HandcraftedNLU
from services.bst import HandcraftedBST
from services.policy import HandcraftedPolicy
from services.nlg import HandcraftedNLG
from services.service import DialogSystem

from utils.logger import DiasysLogger, LogLevel
from services.hci import ConsoleInput, ConsoleOutput
from services.domain_tracker import DomainTracker

from services.service import PublishSubscribe
from services.service import Service
from utils.beliefstate import BeliefState
from utils.topics import Topic
from utils.sysact import SysAct

domain = JSONLookupDomain(name='restaurants_stuttgart')
nlu = HandcraftedNLU(domain=domain)
bst = HandcraftedBST(domain=domain)
d_tracker = DomainTracker(domains=[domain])

user_in = ConsoleInput(domain="")
user_out = ConsoleOutput(domain="")

class BST_Tester(Service):
    def __init__(self, domain=None, logger=None):
        Service.__init__(self, domain=domain)
        self.logger = logger

    @PublishSubscribe(sub_topics=["beliefstate"], pub_topics=["sys_act", "sys_state"])
    def show_bst(self, beliefstate: BeliefState):
        print(beliefstate._history)
        return {'sys_act': "None", "sys_state": "None"}

class Output_Simulator(Service):
    def __init__(self, domain=None, logger=None):
        Service.__init__(self, domain=domain)
        self.logger = logger
    
    @PublishSubscribe(sub_topics=["sys_utterance"], pub_topics=[Topic.DIALOG_END])
    def simulate_output(self, sys_utterance: str = None):
        return {Topic.DIALOG_END: 'bye' in sys_utterance}

class NLG_Simulator(Service):
    def __init__(self, domain=None, logger=None):
        Service.__init__(self, domain=domain)
        self.logger = logger
    
    @PublishSubscribe(sub_topics=["sys_act"], pub_topics=["sys_utterance"])
    def simulate_nlg(self, sys_act: SysAct = None):
        return {'sys_utterance': "None"}

bst_tester = BST_Tester(domain=domain)
output_simulator = Output_Simulator(domain=domain)
nlg_simulator = NLG_Simulator(domain=domain)

logger = DiasysLogger(console_log_lvl=LogLevel.DIALOGS)
ds = DialogSystem(services=[d_tracker, user_in, output_simulator, nlu, bst, bst_tester, nlg_simulator], debug_logger=logger)

error_free = ds.is_error_free_messaging_pipeline()
if not error_free:
    ds.print_inconsistencies()

for _ in range(1):
    ds.run_dialog({'gen_user_utterance': ""})
ds.shutdown()
