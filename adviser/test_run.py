from utils.domain.jsonlookupdomain import JSONLookupDomain
from services.nlu.nlu import HandcraftedNLU
domain = JSONLookupDomain('restaurants_stuttgart')
nlu = HandcraftedNLU(domain=domain)

user_input = input('>>> ')
while user_input.strip().lower() not in ('', 'exit', 'bye', 'goodbye'):
    user_acts = nlu.extract_user_acts(user_input)['user_acts']
    print('\n'.join([repr(user_act) for user_act in user_acts]))
    user_input = input('>>> ')
