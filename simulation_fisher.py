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


def get_parameters(std_util=150, mu_util=500, portion_extra_desire=0.3, factor_mu_extra_desire=200, agents_num=14,
                           missions_num=14, start=0, end=100, termination=1000, type_communication=1, algorithm =1, threshold = 0.00001 ):
    #creator_delay = None
    if type_communication == 1:
        creator_delay = CreatorDelaysEl()

    protocols = creator_delay.create_protocol_delay()

    mailer_params = {'protocols_list': protocols, 'protocol header':creator_delay.header(), 'termination': termination,'algorithm': algorithm}

    fisher_params = {'mu_util': mu_util, 'mu_util_extra_desire': mu_util * factor_mu_extra_desire,
                       'std_util': std_util,"threshold ": threshold}

    algorithm_params = {1: fisher_params}


    problem = {'agents_num': agents_num, 'missions_num': missions_num, 'start': start, 'end': end, 'extra_desire_num': portion_extra_desire * missions_num}






    return mailer_params, algorithm_params, problem

def create_problems(problem_p):
    # parameters for simulation
    start = problem_p['start']
    end = problem_p['end']

    ans = []

    for i in range(start, end):
        problem_i = Problem_Distributed(prob_id=i, agents_num=problem_p['agents_num'], missions_num=problem_p['missions_num'],extra_desire = problem_p['extra_desire_num'] )

        ans.append(problem_i)

    return ans



def create_mailer_given_algo(mailer_parameters, problem, delay_protocol):
    termination = mailer_parameters['termination']
    algorithm_number = mailer_parameters['algorithm']
    if algorithm_number == 1:
        return MailerFisher(termination, problem, delay_protocol)


def solve_problem(problems_created, mailer_params, algo_params_map):
    protocols = mailer_params['protocols_list']
    algorithm_selected_number  = mailer_params['algorithm']
    algorithm_param = algo_params_map[algorithm_selected_number]

    full_data = []
    to_avg_map = {}
    for delay_protocol in protocols:
        mailers_with_same_delay_protocol = []
        for problem in problems_created:
            mailer = create_mailer(mailer_params, problem, algorithm_param, algorithm_selected_number)
            mailer.execute()
            mailers_with_same_delay_protocol.append(mailer.data_map())
            full_data.append(mailer.results)
        to_avg_map[delay_protocol] = mailers_with_same_delay_protocol
    return full_data, to_avg_map

if __name__ == "__main__":
    mailer_params, algorithm_params, problem_params = get_parameters()
    problems = create_problems(problem_p = problem_params)
    full_data, to_avg_map = solve_problem(problems = problems, mailer_params = mailer_params, algo_params_map = algorithm_params)









