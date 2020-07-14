from communication import CreatorDelaysEl, CreatorDelaysNormal
from mailers import MailerIterations
from problem_entities import Problem_Distributed
import statistics
import pandas as pd
from pandas import DataFrame

def get_params_random(portion_extra_desire, missions_num, is_random_input, algorithm, mu_util, factor_mu_extra_desire,
                      std_util):
    ans = {'extra_desire_num': portion_extra_desire * missions_num}

    # algorithm = 1 -> fisher

    if is_random_input:
        if algorithm == 1 or algorithm == 2:
            ans['mu_util'] = mu_util
            ans['mu_util_extra_desire'] = mu_util * factor_mu_extra_desire
            ans['std_util'] = std_util
    else:
        ans = None

    return ans


def algorithm_name(algorithm):
    if algorithm == 1:
        algorithm_name = "Fisher Asynchronous V1"
    if algorithm == 2:
        algorithm_name = "Fisher Asynchronous V2"
    if algorithm == 3:
        algorithm_name = "Fisher Synchronous"
    return  algorithm_name


def get_params_algorithm(algorithm=1, threshold=0.00001, init_option=2, mission_counter_converges= 0, util_type = 0):
    # to create fisher simulator and create random
    ans = {}
    algo_data = [algorithm_name(algorithm)]
    algo_header = ["Algorithm"]


    ans['algorithm_number'] = algorithm
    if algorithm == 1 or algorithm == 2:
        # init_option = 0 -> if x_ij did was not received treat it as 0,
        # init_option = 1 -> if x_ij did was not received treat it as 1,
        # init_option = 2 -> 1/number of missions
        ans['threshold'] = threshold
        ans['init_option'] = init_option
        # util_type = 0 ->
        ans['util_type'] = util_type
        algo_data.append(threshold)
        algo_header.append("Threshold")
    if algorithm == 2:
        ans['mission_counter_converges'] = mission_counter_converges
        algo_data.append(mission_counter_converges)
        algo_header.append("Mission Counter Converges")

    return ans, algo_data, algo_header


def get_params_problem(algorithm, random_params, agents_num, missions_num, start, end, algorithm_params):
    ans = {'algorithm': algorithm, 'random_params': random_params,
           'agents_num': agents_num, 'missions_num': missions_num,
           'start': start, 'end': end, 'algorithm_params': algorithm_params}
    return ans


def get_params_mailer(termination=1000, is_random=True, is_mailer_thread=False, include_data = True):
    ans = {'termination': termination, 'is_random': is_random, 'is_mailer_thread': is_mailer_thread, 'include_data':include_data}
    return ans


def get_protocols(type_communication=1):
    if type_communication == 1:
        creator_delay = CreatorDelaysNormal()
    if type_communication == 2:
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


def create_mailer(problem, delay_protocol, mailer_parameters, debug_print_problem):
    is_mailer_thread = mailer_parameters['is_mailer_thread']
    termination = mailer_parameters['termination']
    is_random = mailer_parameters['is_random']
    agents = problem.agents
    missions = problem.missions
    problem_id = problem.prob_id
    is_include_data = mailer_parameters['include_data']

    if is_mailer_thread:
        print("to do mailer thread")
    else:
        return MailerIterations(problem_id = problem_id,agents=agents, missions=missions, delay_protocol=delay_protocol,
                                termination=termination, debug_print_problem = debug_print_problem, is_random=is_random, is_include_data = is_include_data)

def solve_problems(problems_input, protocols_input, mailer_params, debug_print_problem=False):
    is_include_data = mailer_params['include_data']
    data_per_protocol = {}
    for protocol in protocols_input:
        mailers_with_same_delay_protocol = []
        for problem in problems_input:
            if debug_print_problem:
                problem.print_input()
            mailer = create_mailer(problem=problem, delay_protocol=protocol, mailer_parameters=mailer_params, debug_print_problem = debug_print_problem)
            mailer.execute()
            if is_include_data:
                mailers_with_same_delay_protocol.append(mailer.results)
        data_per_protocol[protocol] = mailers_with_same_delay_protocol
    return data_per_protocol


def get_max_iteration(data_per_protocol):
    ans = {}
    for protocol, list_of_dicts in data_per_protocol.items():
        max_per_protocol_list = []
        for dict_per_mailer in list_of_dicts:
            max_iteration_per_mailer = max(list(dict_per_mailer.keys()))
            max_per_protocol_list.append(max_iteration_per_mailer)
        max_per_protocol_iteration = max(max_per_protocol_list)
        ans[protocol] = max_per_protocol_iteration
    max_of_all = max(list(ans.values()))
    return ans, max_of_all


def get_iteration_for_dict(dict_per_mailer, iteration_current):
    max_per_mailer = max(list(dict_per_mailer.keys()))
    if iteration_current > max_per_mailer:
        ans = max_per_mailer
    else:
        ans = iteration_current
    return ans


def create_mean_data_per_protocol(data_per_protocol, max_per_protocol):
    ans = {}
    for protocol, list_of_dicts in data_per_protocol.items():
        dict_per_protocol_mean = []
        iteration_max = max_per_protocol[protocol]
        for iteration_current in range(1, iteration_max+1):
            rx_bird_eye = []
            rx_agent_view = []
            rx_mono = []
            envy = []
            rx_per_agent_map= {}
            mono_per_agent_rx_weakly_map= {}

            for dict_per_mailer in list_of_dicts:
                iteration_for_dict = get_iteration_for_dict(dict_per_mailer, iteration_current)
                data_object = dict_per_mailer[iteration_for_dict]

                rx_bird_eye.append(data_object.rx_bird_eye_sum)
                rx_agent_view.append(data_object.rx_agent_view_sum)
                rx_mono.append(data_object.mono_global_rx_weakly)
                envy.append(data_object.envy_bird_eye_max)
                #rx_per_agent_map
                #mono_per_agent_rx_weakly
                for agent, personal_rx in data_object.rx_per_agent_map.items():
                    if agent.agent_id not in rx_per_agent_map:
                        rx_per_agent_map[agent.agent_id] = []
                    rx_per_agent_map[agent.agent_id].append(personal_rx)

                for agent, personal_mono in data_object.mono_per_agent_rx_weakly.items():
                    if agent.agent_id not in mono_per_agent_rx_weakly_map:
                        mono_per_agent_rx_weakly_map[agent.agent_id] = []
                    mono_per_agent_rx_weakly_map[agent.agent_id].append(personal_mono)

            results_per_iteration_global = [iteration_current, statistics.mean(rx_bird_eye), statistics.mean(rx_agent_view),
                                     statistics.mean(rx_mono), statistics.mean(envy)]
            mean_per_agent_rx = []
            for agent_id, list_of_rx in rx_per_agent_map.items():
                mean_per_agent_rx.append(statistics.mean(list_of_rx))

            mean_per_agent_mono = []
            for agent_id, list_of_mono in mono_per_agent_rx_weakly_map.items():
                mean_per_agent_mono.append(statistics.mean(list_of_mono))

            results_per_iteration = results_per_iteration_global + mean_per_agent_rx + mean_per_agent_mono

            dict_per_protocol_mean.append(results_per_iteration)
        ans[protocol] = dict_per_protocol_mean

    results_global_header = ["Time", "RX Bird Eye", "RX Agent View", "RX Mono", "Max Envy"]
    personal_rx_header = []
    personal_mono_header = []

    for key in mono_per_agent_rx_weakly_map.keys():
        personal_rx_header.append("RX agent "+str(key))
        personal_mono_header.append("Mono RX agent "+str(key))

    results_header = results_global_header+personal_rx_header+personal_mono_header
    return ans, results_header


def turn_mean_data_per_protocol_to_df(mean_data_per_protocol, header, problem_data):
    ans = {}
    for protocol, mean_results in mean_data_per_protocol.items():
        from_list_to_tuples = []
        protocol_data = protocol.data_of_protocol()
        for result in mean_results:
            from_list_to_tuples.append(tuple(problem_data)+tuple(protocol_data)+tuple(result))
        df = pd.DataFrame(from_list_to_tuples, columns=header)
        ans[protocol] = df
    return ans


def create_global_data(data_per_protocol, protocols_header, problem_header, problem_data):
    max_per_protocol, max_of_all = get_max_iteration(data_per_protocol)
    mean_data_per_protocol, results_header = create_mean_data_per_protocol(data_per_protocol, max_per_protocol)
    header = problem_header + protocols_header + results_header
    return turn_mean_data_per_protocol_to_df(mean_data_per_protocol, header, problem_data)


def get_avg_last_iteration(data_per_protocol):
    ans = {}
    for protocol, list_of_dicts in data_per_protocol.items():
        per_protocol_list = []
        for dict_per_mailer in list_of_dicts:
            max_iteration_per_mailer = max(list(dict_per_mailer.keys()))
            per_protocol_list.append(max_iteration_per_mailer)
        mean_last_iter = statistics.mean(per_protocol_list)
        ans[protocol] = mean_last_iter
    results_header = ["Termination Time"]
    return ans, results_header


def turn_mean_last_iter_to_df(mean_max_iter_per_protocol, header, problem_data):
    list_of_tuples = []
    for protocol, mean_results in mean_max_iter_per_protocol.items():
        protocol_data = protocol.data_of_protocol()
        ttt = tuple([mean_results])
        list_of_tuples.append(tuple(problem_data) + tuple(protocol_data) + ttt)
    return pd.DataFrame(list_of_tuples, columns=header)

def create_last_data(data_per_protocol, protocols_header, problem_header, problem_data):
     mean_max_iter_per_protocol, results_header = get_avg_last_iteration(data_per_protocol)
     header = problem_header + protocols_header + results_header
     return turn_mean_last_iter_to_df(mean_max_iter_per_protocol, header, problem_data)

def create_data(data_per_protocol, protocols_header, problem_header, problem_data):
    df_global_per_protocol = create_global_data(data_per_protocol, protocols_header, problem_header, problem_data)
    df_last_iter = create_last_data(data_per_protocol, protocols_header, problem_header, problem_data)
    return df_global_per_protocol, df_last_iter


def create_csv(df_per_global, df_last_iter, file_name):
    flag = False
    for df_i in df_per_global.values():
        if not flag:
            df = df_i
            flag = True
        else:
            df = df.append(df_i,ignore_index=True)
    df.to_csv("tables\per_iteration, "+file_name, index = False)
    df_last_iter.to_csv("tables\last_iteration, "+file_name, index = False)


def create_file_header(problem_header, problem_data):
    file_name_data = ""
    for i in range(len(problem_header)):
        if i >= len(problem_header)-1 :
            file_name_data = file_name_data + problem_header[i] + "= " + str(problem_data[i])
        else:
            file_name_data = file_name_data + problem_header[i] + "= " + str(problem_data[i]) + ", "

    file_name_data = file_name_data +".csv"
    return file_name_data

if __name__ == "__main__":
    # params_random input from user
    portion_extra_desire_input = 0.3
    std_util_input = 100
    mu_util_input = 500
    factor_mu_extra_desire_input = 2
    is_random_input = True

    # params_algorithm input from user
    algorithm_input = 2 # 1: asynchronous without termination, 2: asynchronous with termination
    init_option_input = 2 # 1:create input from simulation of problem, 2: random

    # Fisher
    threshold_input = 0.001
    util_type_input = 0 # 0: linear util
    # Fisher v2
    mission_counter_converges_input = 5

    # params_problem input from user
    agents_num_input = 4
    missions_num_input = 5
    start_input = 0
    end_input = 1

    # params_mailer input from user
    termination_input = 200
    is_mailer_thread_input = False
    include_data_input = True

    # -----------SET VARIABLES-------------
    type_communication_input = 1

    # -----------FOR DEBUG-----------------
    debug_print_problem = False

    params_random = get_params_random(portion_extra_desire=portion_extra_desire_input, missions_num=missions_num_input,
                                      is_random_input=is_random_input,
                                      algorithm=algorithm_input, mu_util=mu_util_input,
                                      factor_mu_extra_desire=factor_mu_extra_desire_input, std_util=std_util_input)

    params_algorithm, algo_data, algo_header = get_params_algorithm(algorithm=algorithm_input, threshold=threshold_input,
                                            init_option=init_option_input, mission_counter_converges =
                                            mission_counter_converges_input, util_type = util_type_input)

    params_problem = get_params_problem(algorithm=algorithm_input, random_params=params_random,
                                        agents_num=agents_num_input,
                                        missions_num=missions_num_input, start=start_input, end=end_input,
                                        algorithm_params=params_algorithm)
    problem_header = ["Agents","Missions","Start","End"]+algo_header
    problem_data = [agents_num_input, missions_num_input,start_input, end_input]+algo_data

    params_mailer = get_params_mailer(termination=termination_input, is_mailer_thread=is_mailer_thread_input,
                                      is_random=is_random_input, include_data = include_data_input)

    protocols, protocols_header = get_protocols(type_communication=type_communication_input)

    # -----------RUN SIMULATION-------------


    problems = create_problems(problem_p=params_problem)
    data_per_protocol = solve_problems(problems_input = problems, protocols_input = protocols, mailer_params = params_mailer, debug_print_problem = debug_print_problem )
    df_per_global, df_last_iter = create_data(data_per_protocol, protocols_header, problem_header, problem_data)
    file_header = create_file_header(problem_header, problem_data)
    create_csv(df_per_global, df_last_iter, file_name=file_header)

