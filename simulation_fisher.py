import communication as com
import problem_entities as prob

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
                           missions_num=14, start=0,
                           end=100, termination=1000, type_communication=1):
    #creator_delay = None
    if type_communication == 1:
        creator_delay = com.CreatorDelaysEl()

    protocols = creator_delay.create_protocol_delay()
    problem = {'std_util': std_util, 'mu_util': mu_util, 'portion_extra_desire': portion_extra_desire,
               'factor_mu_extra_desire': factor_mu_extra_desire,
               'agents_num': agents_num, 'missions_num': missions_num}

    if creator_delay is None:
        print("type_communication number is not vaild sent to getDefaultParameters method")

    simulator = {'start': start, 'end': end}

    return problem, simulator, termination, protocols


def create_problems(problem_p, simulator_p):
    # parameters for simulation
    start = simulator_p['start']
    end = simulator_p['end']

    ans = []

    for i in range(start, end):
        problem_i = prob.Distributed_Problem(prob_id=i, agents_num=problem_p['agents_num'], missions_num=problem_p['missions_num'],
                                     mu_util=problem_p['mu_util'], std_util=problem_p['std_util'],
                                     portion_extra_desire=problem_p['portion_extra_desire'],
                                     factor_extra_desire=problem_p['factor_mu_extra_desire'])

        ans.append(problem_i)




    return ans


if __name__ == "__main__":
    problem_parameters, simulator_parameters, termination, delay_protocols = get_parameters()
    problems = create_problems(problem_parameters = problem_parameters, simulator_parameters = simulator_parameters)
    algorithm = 1 # 1 = fisher
    mailers_map = {}
    for delay_protocol in delay_protocols:
        mailers_with_same_delay_protocol = []
        for problem in problems:
        mailer = Mailer(delay_protocols, problem.agents, algorithm)
        agents_meet_mailer(mailer, problem.agents)
        mailer.execute()
        mailers_with_same_delay_protocol.append(mailer.data)
    mailers_map[delay_protocol]=mailers_with_same_delay_protocol








