import random
from builtins import print


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
    def __init__(self, agent_id, problem_id=None, ):
        self.problem_id = problem_id
        self.agent_id = agent_id
        self.mission_responsibility = []
        self.msg_time_stamp = 0
        # **fisher fields**

        # *agent fields
        self.r_i = {}
        self.x_i = {}  # msg from mission to agent
        self.message_x_i_received = {}  # msg from mission to agent

        self.bids_to_send = False
        self.allocation_to_send = False
        self.msgs_from_hosted_missions = []



        self.threshold = 0.0001
        self.bid_placed_for_missions = {}





    def reset(self):
        self.mission_responsibility = []
        self.msg_time_stamp = 0

    # 1.3.2 called from mailer, agents reaction to msg increases agent time stamp before sending msgs
    def update_time_stamp(self):
        self.msg_time_stamp = self.msg_time_stamp + 1

    def add_to_task_responsibility(self, mission):
        self.mission_responsibility.append(mission)

    def get_task_responsibility_size(self):
        return len(self.mission_responsibility)

    # 1.1.1 **prepare_algorithm_input**
    # *Fisher*
    # creates random utilities to all missions in list, given if they are more desired, for fisher simulator
    def create_missions_random_utils(self, missions, util_parameters):
        extra_desire_counter = self.problem_id * 100 + self.agent_id * 1000
        standard_desire_counter = self.problem_id * 89 + self.agent_id * 74

        for i in range(len(missions)):
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

            self.r_i[mission] = util

        # 1.1.1 called from prepare_fields,

    # creates utilities to all missions in list from simulator
    def create_missions_utils(self, missions):
        self.r_i = {}
        print("from agent: sofi needs to complete")
        raise NotImplementedError()

    # 1.3.1 **agents_initialize**
    # *Fisher*
    def initialize_fisher(self, threshold1):
        self.init_fields(threshold1=threshold1)
        self.place_initial_bids()

    def init_fields(self, threshold1):
        self.x_i = {}  # msg from mission to agent
        self.message_x_i_received = {}  # msg from mission to agent
        self.msgs_from_hosted_missions = []
        self.threshold = threshold1
        for mission in self.r_i.keys():
            self.x_i[mission] = 0

        self.bids_to_send = False
        self.allocation_to_send = False

    def place_initial_bids(self):
        rx_i = 0
        for mission in self.r_i.keys():
            rx_i = rx_i+self.r_i.get(mission)*1
        denominator = sum(rx_i)
        for mission in self.r_i.keys():
            rx_ij = self.r_i*1
            self.bid_placed_for_missions[mission] = rx_ij / denominator
        self.bids_to_send = True







class Problem(object):

    def __init__(self, prob_id, agents_num, missions_num, extra_desire, is_random_util, fisher_utils_params):
        self.prob_id = prob_id
        self.extra_desire_num = extra_desire

        # generate entities
        self.missions = []
        self.create_missions(missions_num=missions_num)
        self.agents = []
        self.create_agents(agents_num=agents_num)
        if is_random_util:
            for agent in self.agents:
                agent.create_missions_random_utils(util_parameters=fisher_utils_params)

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
            agent = Agent(problem_id=self.prob_id, agent_id=i)
            self.agents.append(agent)

    def __str__(self):
        return str(self.prob_id) + "," + str(self.agents_num) + "," + str(self.missions_num)

    @staticmethod
    def header():
        return "Problem Id,Agents Amount,Missions Amount,Utility Mean, Utility Std, Mean of Missions with Desire, " \
               "Amount of Extra Desire Missions, "


class Problem_Distributed(Problem):

    def __init__(self, prob_id, agents_num, missions_num, extra_desire, is_random_util, fisher_utils_params):
        Problem.__init__(self, prob_id, agents_num, missions_num, extra_desire, is_random_util, fisher_utils_params)

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
                        agent.add_to_task_responsibility(mission=mission)
                        mission.set_assigned_agent(agent)
                        flag = True
                        break
                if not flag:
                    counter = counter + 1
