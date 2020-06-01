from communication import CreatorDelaysEl
from problem_entities import Problem_Distributed


def get_params_random(portion_extra_desire, missions_num, is_random_input, algorithm, mu_util, factor_mu_extra_desire, std_util):
    ans = {'extra_desire_num': portion_extra_desire * missions_num}

    # algorithm = 1 -> fisher

    if is_random_input:
        if algorithm == 1:
            ans['mu_util'] = mu_util
            ans['mu_util_extra_desire'] = mu_util * factor_mu_extra_desire
            ans['std_util'] = std_util
    else:
        ans = None

    return ans


def get_params_algorithm(algorithm=1, threshold= 0.00001, init_option = 2):
    # to create fisher simulator and create random
    ans = {}
    if algorithm == 1:
        # init_option = 0 -> if x_ij did was not received treat it as 0,
        # init_option = 1 -> if x_ij did was not received treat it as 1,
        # init_option = 2 -> 1/number of missions
        ans = {'threshold': threshold, "init_option": init_option}
    return ans


def get_params_problem(algorithm,random_params,agents_num,missions_num,start, end,algorithm_params ):
    ans = {'algorithm': algorithm, 'random_params': random_params,
               'agents_num': agents_num, 'missions_num': missions_num,
               'start': start, 'end': end, 'algorithm_params': algorithm_params}
    return ans


def get_params_mailer( termination=1000, is_random = True):
    ans = {'termination': termination, 'is_random':is_random}
    return ans

def get_protocols( type_communication=1 ):
    if type_communication == 1:
        creator_delay = CreatorDelaysEl()

    return creator_delay.create_protocol_delay(), creator_delay.header()

def create_problems(problem_p):
    algorithm = problem_p['algorithm']
    random_params = problem_p['random_params']
    agents_num = problem_p['agents_num']
    missions_num = problem_p['missions_num']
    start = problem_p['start']
    end = problem_p['end']
    algorithm_params = problem_p['algorithm_params']
    # parameters for simulation
    ans = []
    for i in range(start, end):
        problem_i = Problem_Distributed(prob_id=i,  algorithm = algorithm, random_params = random_params, agents_num = agents_num, missions_num = missions_num, algorithm_params =algorithm_params)
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

# params_random input from user
    portion_extra_desire_input = 0.3
    std_util_input = 150
    mu_util_input = 500
    factor_mu_extra_desire_input = 200
    is_random_input = True

# params_algorithm input from user
    algorithm_input = 1
    threshold_input = 0.00001
    init_option_input = 2

# params_problem input from user
    agents_num_input = 14
    missions_num_input = 14
    start_input = 0
    end_input = 100
    termination_input = 1000

# protocol input from user
    type_communication_input = 1




    params_random = get_params_random(portion_extra_desire = portion_extra_desire_input, missions_num = missions_num_input, is_random_input= is_random_input,
                                      algorithm= algorithm_input, mu_util= mu_util_input, factor_mu_extra_desire= factor_mu_extra_desire_input, std_util= std_util_input)

    params_algorithm = get_params_algorithm(algorithm=algorithm_input, threshold= threshold_input, init_option = init_option_input)

    params_problem = get_params_problem(algorithm = algorithm_input, random_params= params_random ,agents_num = agents_num_input,
                                        missions_num = missions_num_input,start = start_input , end = end_input, algorithm_params =params_algorithm)

    params_mailer = get_params_mailer( termination=termination_input, is_random = is_random_input)

    protocols, protocols_header = get_protocols(type_communication =type_communication_input)




    problems = create_problems(problem_p = problem_parameters)
    full_data, to_avg_map = solve_problem(problems = problems, mailer_params = mailer_params, algo_params_map = algorithm_params, protocols = protocols)









