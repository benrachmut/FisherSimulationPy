import random


class Mission(object):
    def __init__(self, mission_id, extra_desire=False):
        self.mission_id = mission_id
        self.extra_desire = extra_desire
        self.assigned_agent = None

    def reset(self):
        self.assigned_agent = None

    def set_assigned_agent(self, agent):
        self.assigned_agent = agent


class Agent(object):
    def __init__(self, agent_id, problem_id=None, missions=None, util_parameters=None):
        self.problem_id = problem_id
        self.agent_id = agent_id
        self.utils_of_missions = {}
        self.create_utils_of_missions(missions=missions, util_parameters=util_parameters)
        self.taskResponsibility = []


    def reset(self):
        self.taskResponsibility = []

    def add_to_task_responsibility(self, mission):
        self.taskResponsibility.append(mission)

    def get_task_responsibility_size(self):
        return len(self.taskResponsibility)

    def create_utils_of_missions(self, missions, util_parameters):
        extra_desire_counter = self.problem_id * 100 + self.agent_id * 1000
        standard_desire_counter = self.problem_id * 89 + self.agent_id * 74

        for i in len(missions):
            mission = self.missions[i]
            is_mission_extra_desired = mission.extra_desire

            if is_mission_extra_desired:
                extra_desire_counter = extra_desire_counter + 78
                random.seed(extra_desire_counter)
                util = random.gauss(mu=util_parameters['mu_util_extra_desire'], sigma=util_parameters['std_util'])
            else:
                standard_desire_counter = standard_desire_counter + 457
                random.seed(standard_desire_counter)
                util = random.gauss(mu=util_parameters['mu_util'], sigma=util_parameters['std_util'])

            self.utils_of_missions[mission] = util




class Problem(object):

    def __init__(self, prob_id, agents_num, missions_num, mu_util, std_util, portion_extra_desire,
                 factor_mu_extra_desire, ):
        self.prob_id = prob_id
        extra_desire_num = round(agents_num * portion_extra_desire)
        self.util_parameters = {'mu_util': mu_util, 'mu_util_extra_desire': mu_util * factor_mu_extra_desire,
                                'extra_desire_num': extra_desire_num, 'std_util': std_util}

        # generate entities
        self.missions = []
        self.create_missions(missions_num=missions_num)
        self.agents = []
        self.create_agents(agents_num=agents_num)

    def create_missions(self, missions_num):
        counter_extra_desire = self.extra_desire_num
        for i in range(missions_num):
            if counter_extra_desire == 0:
                mission = Mission(mission_id=i, extra_desire=False)
            else:
                counter_extra_desire = counter_extra_desire - 1
                mission = Mission(mission_id=i, extra_desire=True)
            self.missions.append(mission)

    def create_agents(self, agents_num):
        for i in range(agents_num):
            agent = Agent(problem_id=self.prob_id, agent_id=i, missions=self.missions,
                          util_parameters=self.util_parameters)
            self.agents.append(agent)

    def __str__(self):
        return str(self.prob_id) + "," + str(self.agents_num) + "," + str(self.missions_num) + "," + str(
            self.util_parameters['mu_util']) + "," + str(self.util_parameters['std_util']) + "," + str(
            self.util_parameters['mu_util_extra_desire']) + "," + str(self.util_parameters['extra_desire_num'])

    @staticmethod
    def header():
        return "Problem Id,Agents Amount,Missions Amount,Utility Mean, Utility Std, Mean of Missions with Desire, " \
               "Amount of Extra Desire Missions, "


class Distributed_Problem(Problem):

    def __init__(self, prob_id, agents_num, missions_num, mu_util, std_util, portion_extra_desire, factor_extra_desire):
        Problem.__init__(self, prob_id, agents_num, missions_num, mu_util, std_util, portion_extra_desire,
                         factor_extra_desire)
        self.create_agents(agents_num=agents_num)
        self.connect_mission_to_agent(missions_num=missions_num, agent_num=agents_num)

    def connect_mission_to_agent(self, missions_num, agent_num):
        counter = 0
        for i in range(missions_num):
            mission = self.missions[i]
            flag = False
            while not flag:
                for j in range(agent_num):
                    agent = self.agents[j]
                    if agent.get_task_responsibility_size() == counter:
                        agent.add_to_task_responsibility(mission = mission)
                        mission.set_assigned_agent(agent)
                        flag = True
                        break
                if not flag:
                    counter = counter + 1