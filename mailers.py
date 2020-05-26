from abc import ABC

from msgs import Msg, MsgFisherBid
from problem_entities import AgentDistributed


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
    def __init__(self, agents, missions, delay_protocol, termination, is_random):
        self.termination = termination
        self.agents = agents
        self.missions = missions
        self.delay = delay_protocol
        self.msg_box = []
        self.results = {}
        self.receives_in_current_iteration = {}
        self.is_random = is_random
        self.agent_host_missions_map = {}
        self.create_agent_host_missions_map()

    def execute(self):
        for agent in self.agents:
            agent.meet_mailer(self)
        self.prepare_fields()
        self.execute_specific()

    def execute_specific(self):
        raise NotImplementedError()



    def create_agent_host_missions_map(self):
        for agent in self.agents:
            self.agent_host_missions_map[agent] = agent.mission_responsibility

    # ------

    # 1.1 called by execute, actions prior to algorithm simulator
    def prepare_fields(self):

        if not self.is_random:
            for agent in self.agents:
                agent.prepare_algorithm_input()  # abs method, agent prepares input

        for agent in self.agents:
            agent.reset()

        for mission in self.missions:
            mission.reset()

        if isinstance(self.agents[0], AgentDistributed):
            self.agent_host_missions_map = {}
            self.create_agent_host_missions_map()

        self.delay.set_seed()

    # 1.2 called from execute,abs method, create data relevant to algorithm type
    def create_data(self, time):
        self.results[time] = Data()

    def is_terminated(self):  # abs method, is algorithm self terminated before max termination
        for agent in self.agents:
            if not agent.is_terminated():
                return False
        return True

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

    # 1.6.4 called by agents_receive_msgs gets, get agent object for a given agent id
    def get_agent_by_id(self, agent_id):
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        else:
            return None

    # 1.6.2 called by agents_receive_msgs, msg is delivered given msg time stamp
    def an_agent_receive_msgs(self, receiver_agent, msgs_per_agent):
        for msg in msgs_per_agent:
            if not self.delay.is_time_stamp:
                self.agent_receive_a_single_msg(receiver_agent=receiver_agent, msg=msg)
            else:
                time_stamp_held_by_agent = self.get_current_time_stamp(receiver_agent=receiver_agent, msg=msg)
                time_stamp_of_msg_to_be_sent = msg.time_stamp
                if time_stamp_held_by_agent < time_stamp_of_msg_to_be_sent:
                    receiver_agent.agent_receive_a_single_msg(msg=msg)


# ------------

class MailerIterations(Mailer):
    def __init__(self, agents, missions, delay_protocol, termination, is_random):
        Mailer.__init__(self, agents, missions, delay_protocol, termination, is_random)

    # ---------
    # 1. initiate the simulator
    def execute_specific(self):

        for iteration in range(1, self.termination):
            self.agents_react_to_msgs(iteration)
            self.create_data(iteration)
            if self.is_terminated():
                break
            msgs_to_send = self.handle_msgs()
            self.agents_receive_msgs(msgs_to_send)

    def agents_react_to_msgs(self, iteration):
        for agent in self.agents:
            if iteration == 0:
                agent.initialize()
            else:
                if agent in self.receives_in_current_iteration():
                    agent.reaction_to_algorithmic_msgs(agent)

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

    # ---------
