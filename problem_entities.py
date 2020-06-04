import random
from builtins import print

from msgs import MsgFisherBid, MsgFisherAllocation, MsgFisherMissionConverge


class Mission(object):
    def __init__(self, mission_id, extra_desire=False):
        self.mission_id = mission_id
        self.extra_desire = extra_desire
        self.assigned_agent = None
        # fisher
        self.bids = {}
        self.message_bids_received = {}  # msg from mission to agent
        self.allocation_placed_for_agents = {}
        self.termination_flag = False
        self.price = 0
        self.threshold = 0

    def reset(self):
        self.message_bids_received = {}  # msg from mission to agent
        self.bids={}
        self.allocation_placed_for_agents = {}
        self.price = 0
        self.termination_flag = False

    def set_assigned_agent(self, agent):
        self.assigned_agent = agent

    def update_threshold(self, threshold_input):
        self.threshold = threshold_input

    def receive_a_single_msg_bid(self, msg):
        self.bids[msg.sender_id] = msg.context
        self.message_bids_received = msg


    def compute_fisher(self):
        if self.have_bid_zero():
            return False
        else:
            price_t_minus1 = self.price
            self.calculate_price()
            if abs(price_t_minus1 - self.price) <= self.threshold:
                self.termination_flag = True
            for key, bid in self.bids.items():
                self.allocation_placed_for_agents[key] = bid / self.price
            return True

    def have_bid_zero(self):
        for bid in self.bids.values():
            if bid == 0:
                return True
        return False

    def calculate_price(self):
        self.price = 0
        for bid in self.bids.values():
            self.price = self.price + bid

    def set_initial_bid(self, init_value, agent_ids):
        for agent_id in agent_ids:
            self.bids[agent_id] = init_value

    def get_time_stamp(self, sender_id):
        if sender_id in self.message_bids_received:
            return self.message_bids_received.get(sender_id)
        else:
            return -1


    #called by agent that hosts the mission that updates the bid for the mission
    def update_bid_directly(self, agent_id, bid):
        if agent_id != self.assigned_agent.agent_id:
            print("from update_bid_directly in mission something with assigning agent for mission is wrong")
        else:
            self.bids[agent_id] = bid


class Agent(object):
    def __init__(self, agent_id, problem_id=None):
        self.problem_id = problem_id
        self.agent_id = agent_id
        self.msg_time_stamp = 0
        self.mission_responsibility = []
        self.mailer = None
        self.agent_host_missions_map = {}

    ###-------------

    # called by mailer to create a map with all resposibilty ids
    def get_mission_responsibility_ids(self):
        ans = []
        for mission in self.mission_responsibility:
            ans.append(mission.mission_id)
        return ans

    def inform_agent_host_missions_map(self, map_input):
        self.agent_host_missions_map = map_input

    def meet_mailer(self, mailer_input):
        self.mailer = mailer_input

    # called by mailer when trying to gi
    def get_current_time_stamp(self, msg):
        raise NotImplementedError()

    # 1 - prepare algorithms input such as mission's utilities
    def prepare_algorithm_input(self):
        raise NotImplementedError()

    def reset(self):
        self.msg_time_stamp = 0
        self.reset_specific()

    # 2 - reset fields of specific algorithm
    def reset_specific(self):
        raise NotImplementedError()

    # 3 - initialize algorithm, the algorithms first iteration
    def initialize(self):
        raise NotImplementedError()

    def reaction_to_algorithmic_msgs(self):
        self.compute()
        self.msg_time_stamp = self.msg_time_stamp + 1
        self.send_msgs()

    # 4 - after context was updated in method agent_receive_a_single_msg
    def compute(self):
        raise NotImplementedError()

    # 5- after computation broadcast the new information
    def send_msgs(self):
        raise NotImplementedError()

    def is_terminated(self):
        raise NotImplementedError()

    def agent_receive_a_single_msg(self, msg):
        raise NotImplementedError()

    ###-------------Called from problem

    def add_to_task_responsibility(self, mission):
        self.mission_responsibility.append(mission)

    def get_task_responsibility_size(self):
        return len(self.mission_responsibility)



    #called from send_bids where agent wants to send bid for mission it needs to find which agent holds the mission
    # returns that agent's id
    def get_receiver_id(self, mission_id):
        for agent_id, missions_ids in self.agent_host_missions_map.items():
            for i in missions_ids:
                if i == mission_id:
                    return agent_id
        print("in get get_receiver_id in class agent, cannot find mission id in any of the hosted missions")


class AgentFisher(Agent):
    def __init__(self, agent_id, threshold, init_option, problem_id=None):
        Agent.__init__(self, agent_id, problem_id)

        self.init_option = init_option

        self.is_fisher_phase_I = True
        self.r_i = {}
        self.x_i = {}  # msg from mission to agent
        self.message_x_i_received = {}  # msg from mission to agent

        self.flag_bids_to_send = False
        self.flag_allocation_to_send_map = {}
        self.reset_flag_allocation_to_send_map()

        self.flag_bids_receive_map = {}
        self.reset_flag_bids_receive_map()
        self.flag_allocation_receive = False

        # self.msgs_from_hosted_missions = []
        self.threshold = threshold
        self.reset_mission_threshold(self.threshold)
        self.bid_placed_for_missions = {}
        self.mission_price_converge = []

    # called from problem creator
    def create_missions_random_utils(self, missions, util_parameters):
        extra_desire_counter = self.problem_id * 100 + self.agent_id * 1000
        standard_desire_counter = self.problem_id * 89 + self.agent_id * 74
        for i in range(len(missions)):
            mission = missions[i]
            is_mission_extra_desired = mission.extra_desire
            if is_mission_extra_desired:
                extra_desire_counter = extra_desire_counter + 78
                random.seed(extra_desire_counter)
                util = random.gauss(mu=util_parameters['mu_util_extra_desire'], sigma=util_parameters['std_util'])
            else:
                standard_desire_counter = standard_desire_counter + 457
                random.seed(standard_desire_counter)
                util = random.gauss(mu=util_parameters['mu_util'], sigma=util_parameters['std_util'])
            self.r_i[mission.mission_id] = util

    # reset specific
    def reset_specific(self):
        self.x_i = {}  # msg from mission to agent
        self.message_x_i_received = {}  # msg from mission to agent
        # self.msgs_from_hosted_missions = []

        if self.init_option == 2:
            self.init_option = len(self.r_i.keys())

        for mission in self.mission_responsibility:
            mission.set_initial_bid(init_value=self.init_option, agent_ids=self.r_i.keys())

        self.flag_allocation_receive = False
        self.flag_bids_to_send = False
        self.reset_flag_allocation_to_send_map()
        self.reset_flag_bids_receive_map()
        self.is_fisher_phase_I = True
        self.mission_price_converge = []
        for mission in self.mission_responsibility:
            mission.reset()

    def reset_mission_threshold(self, threshold):
        for mission in self.mission_responsibility:
            mission.update_threshold(threshold)

    def reset_flag_allocation_to_send_map(self):
        for mission in self.mission_responsibility:
            self.flag_allocation_to_send_map[mission] = False

    def reset_flag_bids_receive_map(self):
        for mission in self.mission_responsibility:
            self.flag_bids_receive_map[mission] = False

    # initialize
    def initialize(self):
        denominator = sum(self.r_i.values())
        for mission_id, util in self.r_i.items():
            self.bid_placed_for_missions[mission_id] = util / denominator
        #print("money agent a_"+str(self.agent_id)+" spent is:"+str(sum(self.bid_placed_for_missions.values())))
        self.flag_bids_to_send = True

    # creates utilities to all missions in list from simulator
    def prepare_algorithm_input(self, missions):
        self.r_i = {}
        print("from agent: sofi needs to complete")
        raise NotImplementedError()

    def agent_receive_a_single_msg(self, msg):
        mission_id = msg.mission_receiver_id
        if isinstance(msg, MsgFisherBid):
            mission = self.find_hosted_mission_by_id(mission_id=mission_id)
            mission.receive_a_single_msg_bid(msg)
            self.flag_bids_receive_map[mission] = True
        if isinstance(msg, MsgFisherAllocation):
            x_ij = msg.context
            self.x_i[msg.sender_id] = x_ij
            self.message_x_i_received[msg.sender_id] = msg
            self.flag_allocation_receive = True
        if isinstance(msg, MsgFisherMissionConverge):
            self.mission_price_converge.append(msg.mission_sender_id)

    def find_hosted_mission_by_id(self, mission_id):
        for m in self.mission_responsibility:
            if m.mission_id == mission_id:
                return m
        print("agent " + str(self.agent_id) + " is not hosting good number: " + str(mission_id))

    def is_terminated(self):
        for mission_id in self.r_i.keys():
            if mission_id in self.mission_price_converge == False:
                return False
        return True

    def compute(self):
        if self.flag_allocation_receive:
            self.compute_fisher()
            self.flag_allocation_receive = False
            self.flag_bids_to_send = True

        for key, value in self.flag_bids_receive_map.items():
            mission = key
            flag = value
            if flag:
                did_compute = mission.compute_fisher()
                self.flag_bids_receive_map[mission] = False
                if did_compute:
                    self.flag_allocation_to_send_map[mission] = True
                else:
                    self.flag_allocation_to_send_map[mission] = False


    def compute_fisher(self):
        denominator = 0
        for mission_id in self.r_i.keys():
            denominator = denominator + self.r_i.get(mission_id) * self.x_i.get(mission_id)
        for mission_id in self.r_i.keys():
            rx_ij = self.r_i.get(mission_id) * self.x_i.get(mission_id)
            self.bid_placed_for_missions[mission_id] = rx_ij / denominator

    def send_msgs(self):
        if self.flag_bids_to_send:
            self.send_bids()
            self.flag_bids_to_send = False
        for key, value in self.flag_allocation_to_send_map.items():
            mission_id = key
            is_flag_allocation_to_send = value
            if is_flag_allocation_to_send:
                self.send_allocation(mission_id)
                self.flag_allocation_to_send_map[key] = False

    def send_bids(self):
        for mission_id , bid in self.bid_placed_for_missions.items():
            flag_send_bids = False
            for mission in self.mission_responsibility:
                if mission.mission_id == mission_id:
                    mission.update_bid_directly(agent_id = self.agent_id, bid = bid)
                    flag_send_bids = True
            if not flag_send_bids:
                receiver_id = self.get_receiver_id(mission_id = mission_id)
                msg = MsgFisherBid(sender_id=self.agent_id, context=bid, time_stamp=self.msg_time_stamp, mission_receiver_id= mission_id,receiver_id=receiver_id )
                self.mailer.send_msg(msg)
            #class MsgFisherBid(MsgFisher):
                #def __init__(self, sender_id, context, time_stamp, mission_receiver_id, receiver_id=None):





    def get_current_time_stamp(self, msg):
        ans = 0
        if isinstance(msg, MsgFisherBid):
            flag = False
            for mission in self.mission_responsibility:
                if mission.mission_id == msg.mission_receiver_id:
                    mission.get_time_stamp(msg)
                    flag = True
            if not flag:
                print("the destination of msg in not correct")

        if isinstance(msg, MsgFisherAllocation):
            if msg.sender_id in self.message_x_i_received:
                ans = self.message_x_i_received.get(msg.sender_id).time_stamp
            else:
                ans = -1
        return ans



class Problem(object):
    def __init__(self, prob_id, algorithm, random_params, agents_num, missions_num, algorithm_params):

        self.prob_id = prob_id
        # self.algorithm = algorithm
        self.extra_desire_num = 0
        if random_params is not None:
            self.extra_desire_num = random_params['extra_desire_num']
        # generate entities
        self.missions = []
        self.create_missions(missions_num=missions_num)
        self.agents = []
        self.create_agents(agents_num=agents_num, algorithm=algorithm, algorithm_params=algorithm_params)

        if random_params is not None:
            for agent in self.agents:
                agent.create_missions_random_utils(util_parameters=random_params, missions = self.missions)

    def create_missions(self, missions_num):
        counter_extra_desire = self.extra_desire_num
        for i in range(missions_num):
            if counter_extra_desire < 0:
                mission = Mission(mission_id=i, extra_desire=False)
            else:
                counter_extra_desire = counter_extra_desire - 1
                mission = Mission(mission_id=i, extra_desire=True)
            self.missions.append(mission)

    def create_agents(self, agents_num, algorithm, algorithm_params):
        for i in range(agents_num):
            if algorithm == 1:
                agent = AgentFisher(problem_id=self.prob_id, agent_id=i, threshold=algorithm_params['threshold'],
                                    init_option=algorithm_params["init_option"])
            self.agents.append(agent)

    def __str__(self):
        return str(self.prob_id) + "," + str(self.agents_num) + "," + str(self.missions_num)

    @staticmethod
    def header():
        return "Problem Id,Agents Amount,Missions Amount,Utility Mean, Utility Std, Mean of Missions with Desire, " \
               "Amount of Extra Desire Missions, "

    def agents_meet_mailer(self, mailer):
        for agent in self.agents:
            agent.meet_mailer(mailer)


class Problem_Distributed(Problem):
    def __init__(self, prob_id, algorithm, random_params, agents_num, missions_num, algorithm_params):
        Problem.__init__(self, prob_id, algorithm, random_params, agents_num, missions_num, algorithm_params)
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


