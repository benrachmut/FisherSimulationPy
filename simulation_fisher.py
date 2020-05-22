from communication import CreatorDelaysEl
from mailers import MailerFisher
from problem_entities import Problem_Distributed

'''
market parameters:
std_util = std for normal random r_ij
mu_util = mean for normal random r_ij

buyers_num= number of buyers in the market
goods_num =  number of goods in the market
portion_extra_desire = out of goods number how many are extra desired 
factor_extra_desire = shift in mu for extra desired goods


mailer parameters:
start= the first id of market, end= the last id of market --> end-start = number of repetitions
termination= number of iterations to termination
type_communication= 1 is the requested, add more in the future in script communication

'''


def get_parameters( agents_num=14, missions_num=14, start=0, end=100, termination=1000, type_communication=1, algorithm =1,
                    threshold = 0.00001, std_util=150, mu_util=500, portion_extra_desire=0.3, factor_mu_extra_desire=200,is_random_util = True ):
    #creator_delay = None
    if type_communication == 1:
        creator_delay = CreatorDelaysEl()

    protocols = creator_delay.create_protocol_delay()

    mailer_params = {'protocol header':creator_delay.header(), 'termination': termination,'algorithm': algorithm}


    fisher_utils_params = {'mu_util': mu_util, 'mu_util_extra_desire': mu_util * factor_mu_extra_desire,
                       'std_util': std_util}

    fisher_params = {'is_random_util':is_random_util,'threshold': threshold}

    algorithm_params = {1: fisher_params}


    problem = {'is_random_util':is_random_util,'random_utils_parameters':fisher_utils_params,'agents_num': agents_num, 'missions_num': missions_num, 'start': start, 'end': end, 'extra_desire_num': portion_extra_desire * missions_num}

    return mailer_params, algorithm_params, problem, protocols

def create_problems(problem_p):
    # parameters for simulation
    start = problem_p['start']
    end = problem_p['end']
    ans = []
    for i in range(start, end):
        problem_i = Problem_Distributed(prob_id=i, agents_num=problem_p['agents_num'], missions_num=problem_p['missions_num'],extra_desire = problem_p['extra_desire_num'],
                                        is_random_util= problem_p['is_random_util'],fisher_utils_params = problem_p['random_utils_parameters'] )
        ans.append(problem_i)
    return ans

def create_mailer(agents, missions, delay_protocol, mailer_parameters ,algorithms_parameters):
    termination = mailer_parameters['termination']
    algorithm_number = mailer_parameters['algorithm']
    single_algorithm_parameters = algorithms_parameters[algorithm_number]

    if algorithm_number == 1:
        is_random_util = single_algorithm_parameters['is_random_util']
        threshold = single_algorithm_parameters['threshold']

        return MailerFisher(agents = agents, missions = missions, delay_protocol= delay_protocol, termination= termination, threshold = threshold, is_random_util = is_random_util)


def solve_problem( problems , mailer_params, algorithm_params, protocols):

    to_avg_map = {}
    for delay_protocol in protocols:
        mailers_with_same_delay_protocol = []
        for problem in problems:
            mailer = create_mailer(agents = problem.agents, missions=problem.missions, delay_protocol = delay_protocol,mailer_parameters = mailer_params, mailer_parameters = algorithm_params)
            problem.agents_meet_mailer(mailer) # TODO
            mailer.execute()
            mailers_with_same_delay_protocol.append(mailer.data_map())
        to_avg_map[delay_protocol] = mailers_with_same_delay_protocol
    return to_avg_map

if __name__ == "__main__":
    mailer_params, algorithm_params, problem_params, protocols = get_parameters()
    problems = create_problems(problem_p = problem_params)
    full_data, to_avg_map = solve_problem(problems = problems, mailer_params = mailer_params, algo_params_map = algorithm_params, protocols = protocols)









