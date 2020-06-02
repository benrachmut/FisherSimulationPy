from communication import CreatorDelaysEl
from mailers import MailerIterations
from problem_entities import Problem_Distributed


def get_params_random(portion_extra_desire, missions_num, is_random_input, algorithm, mu_util, factor_mu_extra_desire,
                      std_util):
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


def get_params_algorithm(algorithm=1, threshold=0.00001, init_option=2):
    # to create fisher simulator and create random
    ans = {}
    ans['algorithm_number'] = algorithm
    if algorithm == 1:
        # init_option = 0 -> if x_ij did was not received treat it as 0,
        # init_option = 1 -> if x_ij did was not received treat it as 1,
        # init_option = 2 -> 1/number of missions
        ans['threshold'] = threshold
        ans['init_option'] = init_option

    return ans


def get_params_problem(algorithm, random_params, agents_num, missions_num, start, end, algorithm_params):
    ans = {'algorithm': algorithm, 'random_params': random_params,
           'agents_num': agents_num, 'missions_num': missions_num,
           'start': start, 'end': end, 'algorithm_params': algorithm_params}
    return ans


def get_params_mailer(termination=1000, is_random=True, is_mailer_thread=False):
    ans = {'termination': termination, 'is_random': is_random, 'is_mailer_thread': is_mailer_thread}
    return ans


def get_protocols(type_communication=1):
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
        problem_i = Problem_Distributed(prob_id=i, algorithm=algorithm, random_params=random_params,
                                        agents_num=agents_num, missions_num=missions_num,
                                        algorithm_params=algorithm_params)

        # print("------**id of problem : " + str(problem_i.prob_id) + "**--------")
        # for agent in problem_i.agents:
        #     print("--- r_" + str(agent.agent_id))
        #     print(agent.r_i)

        ans.append(problem_i)
    return ans


def create_mailer(problem, delay_protocol, mailer_parameters):
    is_mailer_thread = mailer_parameters['is_mailer_thread']
    termination = mailer_parameters['termination']
    is_random = mailer_parameters['is_random']
    agents = problem.agents
    missions = problem.missions
    problem_id = problem.prob_id

    if is_mailer_thread:
        print("to do mailer thread")
    else:
        return MailerIterations(problem_id = problem_id,agents=agents, missions=missions, delay_protocol=delay_protocol,
                                termination=termination, is_random=is_random)


def solve_problems(problems_input, protocols_input, mailer_params):
    problems_solved_per_protocol = {}
    for protocol in protocols_input:
        mailers_with_same_delay_protocol = []
        for problem in problems_input:
            mailer = create_mailer(problem=problem, delay_protocol=protocol, mailer_parameters=mailer_params)
            mailer.execute()
            mailers_with_same_delay_protocol.append(mailer.data_map())
        problems_solved_per_protocol[protocol] = mailers_with_same_delay_protocol
    return problems_solved_per_protocol


if __name__ == "__main__":
    # params_random input from user
    portion_extra_desire_input = 0.3
    std_util_input = 100
    mu_util_input = 500
    factor_mu_extra_desire_input = 2
    is_random_input = True

    # params_algorithm input from user
    algorithm_input = 1
    threshold_input = 0.00001
    init_option_input = 2

    # params_problem input from user
    agents_num_input = 5
    missions_num_input = 5
    start_input = 0
    end_input = 2

    #
    termination_input = 1000
    is_mailer_thread_input = False
    # -----------SET VARIABLES-------------
    type_communication_input = 1

    params_random = get_params_random(portion_extra_desire=portion_extra_desire_input, missions_num=missions_num_input,
                                      is_random_input=is_random_input,
                                      algorithm=algorithm_input, mu_util=mu_util_input,
                                      factor_mu_extra_desire=factor_mu_extra_desire_input, std_util=std_util_input)

    params_algorithm = get_params_algorithm(algorithm=algorithm_input, threshold=threshold_input,
                                            init_option=init_option_input)

    params_problem = get_params_problem(algorithm=algorithm_input, random_params=params_random,
                                        agents_num=agents_num_input,
                                        missions_num=missions_num_input, start=start_input, end=end_input,
                                        algorithm_params=params_algorithm)

    params_mailer = get_params_mailer(termination=termination_input, is_mailer_thread=is_mailer_thread_input,
                                      is_random=is_random_input)

    protocols, protocols_header = get_protocols(type_communication=type_communication_input)

    # -----------RUN SIMULATION-------------

    problems = create_problems(problem_p=params_problem)
    full_data, to_avg_map = solve_problems(problems_input = problems, protocols_input = protocols, mailer_params = params_mailer)
