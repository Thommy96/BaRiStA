from utils.domain.jsonlookupdomain import JSONLookupDomain
from services.nlu import HandcraftedNLU
from services.bst import HandcraftedBST
from services.policy import HandcraftedPolicy
from services.nlg import HandcraftedNLG
from services.service import DialogSystem

from utils.logger import DiasysLogger, LogLevel
from services.hci import ConsoleInput, ConsoleOutput
from services.domain_tracker import DomainTracker

domain = JSONLookupDomain(name='restaurants_stuttgart')
nlu = HandcraftedNLU(domain=domain)
bst = HandcraftedBST(domain=domain)
policy = HandcraftedPolicy(domain=domain)
nlg = HandcraftedNLG(domain=domain)
d_tracker = DomainTracker(domains=[domain])

user_in = ConsoleInput(domain="")
user_out = ConsoleOutput(domain="")

logger = DiasysLogger(console_log_lvl=LogLevel.DIALOGS)
ds = DialogSystem(services=[d_tracker, user_in, user_out, nlu, bst, policy, nlg], debug_logger=logger)

error_free = ds.is_error_free_messaging_pipeline()
if not error_free:
    ds.print_inconsistencies()

for _ in range(1):
    ds.run_dialog({'gen_user_utterance': ""})
ds.shutdown()
