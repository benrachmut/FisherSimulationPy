from abc import ABC

from msgs import Msg, MsgFisherBid


class Data(object):
    def __init__(self, iteration, agents, missions):
        self.iteration = iteration
        self.sum_rx = calc_sum_rx(agents, missions)
        self.is_envy_free = calc_is_envy_free(agents, missions)
        self.envy_free_score = 0
        if self.is_envy_free == 0:
            self.envy_free_score = calc_envy_free_score(agents, missions)
        self.is_full_iteration = calc_is_full_iteration(agents)
        self.is_end_phase_one(agents)


class Mailer(object):
    def __init__(self, agents, missions, delay_protocol, termination):
        self.termination = termination
        self.agents = agents
        self.missions = missions
        self.delay = delay_protocol
        self.msg_box = []
        self.results = {}
        self.receives_in_current_iteration = {}


class MailerDistributed(Mailer):
    def __init__(self, agents, missions, delay_protocol, termination):
        Mailer.__init__(self, agents, missions, delay_protocol, termination)
        self.agent_host_missions_map = {}
        self.create_agent_host_missions_map()

    def create_agent_host_missions_map(self):
        for agent in self.agents:
            self.agent_host_missions_map[agent] = agent.mission_responsibility

    # 1. initiate the simulator
    def execute(self):
        self.prepare_fields()

        for iteration in range(1, self.termination):
            self.agents_react_to_msgs(
                iteration)  # if iteration == 0 each agent initialize(agent) else each agent reacts to msgs in its context
            self.create_data(iteration)  # abs method, create data relevant to algorithm type
            if self.is_terminated():  # abs method, is algorithm self terminated before max termination
                break
            msgs_to_send = self.handle_msgs()  # decrease msg delay by 1 and return map by receivers
            self.agents_receive_msgs(msgs_to_send)  # agents update their context # TO DO

    # 1.1 called by execute, actions prior to algorithm simulator
    def prepare_fields(self):
        for agent in self.agents:
            self.prepare_algorithm_input(agent)  # abs method, agent prepares input
            agent.reset()
        for mission in self.missions:
            mission.reset()
        self.delay.set_seed()

    # 1.1.1 called from prepare_fields, abs method, agent prepares input
    def prepare_algorithm_input(self, agent):
        raise NotImplementedError()

    # 1.2 called from execute,abs method, create data relevant to algorithm type
    def create_data(self, iteration):
        raise NotImplementedError()

    # 1.3 called by execute, iteration == 0 each agent initialize(agent) else each agent reacts to msgs in its context
    def agents_react_to_msgs(self, iteration):
        for agent in self.agents:
            if iteration == 0:
                self.agents_initialize(agent)
            else:
                if agent in self.receives_in_current_iteration:
                    self.reaction_to_algorithmic_msgs(agent)

    # 1.3.1 called from agents_react_to_msgs, abs method, first iteration that initialize the algorithm
    def agents_initialize(self, agent):
        raise NotImplementedError()

    # 1.3.2 called from agents_react_to_msgs, agents reaction to msg
    def reaction_to_algorithmic_msgs(self, agent):
        self.compute(agent)
        agent.update_time_stamp()
        self.send_msgs(agent)

    # 1.3.2.1 called from reaction_to_algorithmic_msgs, abs method, agent's computation due to new information
    def compute(self, agent):
        raise NotImplementedError()

    # 1.3.2.2 called from reaction_to_algorithmic_msgs, abs method, agent's send msg after computation
    def send_msgs(self, agent):
        raise NotImplementedError()

    # 1.4 called from execute,abs method, check if algorithm converges
    def is_terminated(self):
        raise NotImplementedError()

    # 1.5 called by execute, decrease msg delay by 1 and return map by receivers, returns msgs with no delay
    def handle_msgs(self):
        sorted_msgs = sorted(self.msg_box, key=Msg.comparator_by_msg_delay)
        ans = []
        for i in range(len(sorted_msgs)):
            msg = sorted_msgs[i]
            if msg.delay == 0:
                ans.append()
            else:
                msg.delay = msg.delay - 1
        self.msg_box = [i for i in self.msg_box if i.delay != 0]
        return ans

    # 1.6 called by execute, organize the messages in a map. the key is the receiver and the values are the msgs received
    def agents_receive_msgs(self, msgs_to_send):
        self.create_map_by_receiver(msgs_to_send)
        for key, value in self.receives_in_current_iteration.items():
            msgs_per_agent = value
            receiver_agent = self.get_agent_by_id(key)
            if receiver_agent is None:
                print("in Mailer, agents_receive_msg did not find agent by id")
            self.an_agent_receive_msgs(receiver_agent, msgs_per_agent)

    # 1.6.1 called by agents_receive_msgs organize the messages in a map, key = receiver agent, value = msgs list
    def create_map_by_receiver(self, msgs_to_send):
        self.receives_in_current_iteration = {}
        for msg in msgs_to_send:
            receiver = msg.receiver_id
            if receiver not in self.receives_in_current_iteration:
                self.receives_in_current_iteration[receiver] = []
            self.receives_in_current_iteration[receiver].append(msg)

    # 1.6.2 called by agents_receive_msgs, msg is delivered given msg time stamp
    def an_agent_receive_msgs(self, receiver_agent, msgs_per_agent):
        for msg in msgs_per_agent:
            if not self.delay.is_time_stamp:
                self.agent_receive_a_single_msg(receiver_agent=receiver_agent, msg=msg)
            else:
                time_stamp_held_by_agent = self.get_current_time_stamp(receiver_agent=receiver_agent, msg=msg)
                time_stamp_of_msg_to_be_sent = msg.time_stamp
                if time_stamp_held_by_agent < time_stamp_of_msg_to_be_sent:
                    self.agent_receive_a_single_msg(receiver_agent=receiver_agent, msg=msg)

    # 1.6.2.1 called from an_agent_receive_msgs, abs method, agent current time stamp already in context from agent
    def agent_receive_a_single_msg(self, receiver_agent, msg):
        raise NotImplementedError()

    # 1.6.3 an_agent_receive_msgs, abs method, get time stamp from relevant context
    def get_current_time_stamp(self, receiver_agent, msg):
        raise NotImplementedError()

    # 1.6.4 called by agents_receive_msgs gets, get agent object for a given agent id
    def get_agent_by_id(self, agent_id):
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        else:
            return None


class MailerFisher(MailerDistributed):
    def __init__(self, agents, missions, delay_protocol, termination, threshold, is_random_util):
        Mailer.__init__(self, agents, missions, delay_protocol, termination)
        self.threshold = threshold
        self.is_random_util = is_random_util

    # 1.1.1 called from prepare_fields, abs method, agent prepares input, utilities for each mission
    def prepare_algorithm_input(self, agent):
        if not self.is_random_util:
            print("from mailer: sofi needs to complete")
            raise NotImplementedError()
            agent.create_missions_utils(self, missions=self.missions)

    # 1.2 called from execute, create data relevant to algorithm type
    def create_data(self, iteration):
        self.results[iteration] = DataFisher(iteration, self.agents, self.missions)

    # 1.3.1 called from agents_react_to_msgs, first iteration that initialize the algorithm agent send
    def agents_initialize(self, agent):
        agent.initialize_fisher(self.threshold)

    # 1.3.2.1 called from reaction_to_algorithmic_msgs, abs method, agent's computation due to new information
    #def compute(self, agent)

    # 1.3.2.2 called from reaction_to_algorithmic_msgs, abs method, agent's send msg after computation
    #def send_msgs(self, agent)

    # 1.4 called from execute,abs method, check if algorithm converges
    #def is_terminated(self)

    # 1.6.2.1 called from an_agent_receive_msgs, abs method, agent current time stamp already in context from agent
    def agent_receive_a_single_msg(self, receiver_agent, msg):

        if isinstance(msg, MsgFisherBid):
            receiver_id = get_reciever
            for  key, value in self.agent_host_missions_map.items():
                agent = key
                missions = value
                for mission in missions:
                    if mission.mission_id == msg.mission_receiver_id:
                        agent.agent_id
            msg.receiver_id

    # 1.6.3 an_agent_receive_msgs, abs method, get time stamp from relevant context
    #def get_current_time_stamp(self, receiver_agent, msg)



