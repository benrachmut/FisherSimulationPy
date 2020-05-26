from communication import CreatorDelaysEl
from problem_entities import Problem_Distributed




def get_parameters( agents_num=14, missions_num=14, start=0, end=100, termination=1000, type_communication=1, algorithm =1,
                    threshold = 0.00001, std_util=150, mu_util=500, portion_extra_desire=0.3, factor_mu_extra_desire=200,
                    is_random_input = True, init_option = 1):
    random_params={'extra_desire_num': portion_extra_desire * missions_num}

    # algorithm = 1 -> fisher

    if is_random_input:
        if algorithm == 1:
            random_params['mu_util']=mu_util
            random_params['mu_util_extra_desire']=mu_util * factor_mu_extra_desire
            random_params['std_util']=std_util
    else:
        random_params = None

    algorithm_params = {}
    if algorithm == 1:
        # init_option = 0 -> if x_ij did was not received treat it as 0,
        # init_option = 1 -> if x_ij did was not received treat it as 1,

        algorithm_params = {'threshold': threshold, "init_option":init_option}

    problem = {'algorithm': algorithm,'random_params':random_params,
               'agents_num': agents_num, 'missions_num': missions_num,
               'start': start, 'end': end, 'algorithm_params':algorithm_params}

    if type_communication == 1:
        creator_delay = CreatorDelaysEl()

    #creator_delay = None
    if type_communication == 1:
        creator_delay = CreatorDelaysEl()

    protocols = creator_delay

    mailer_params = {'termination': termination, 'is_random_input':is_random_input}

    return problem

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
    problem_parameters = get_parameters()
    problems = create_problems(problem_p = problem_parameters)
    full_data, to_avg_map = solve_problem(problems = problems, mailer_params = mailer_params, algo_params_map = algorithm_params, protocols = protocols)









