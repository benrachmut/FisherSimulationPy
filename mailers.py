from msgs import Msg

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
    def __init__(self, termination, agents, missions, delay_protocol):
        self.termination = termination
        self.agents = agents
        self.missions = missions
        self.delay = delay_protocol
        self.msg_box = []
        self.results = {}
        self.receives_in_current_iteration = {}

    def prepare_fields(self):
        for agent in self.agents:
            self.prepare_algorithm_input(agent)  # abs method, agent prepares input
            agent.reset()
        for mission in self.missions:
            mission.reset()
        self.delay.set_seed()





    def execute(self):
        self.prepare_fields()

        for iteration in range(1, self.termination):
            self.agents_react_to_msgs(iteration)  # if iteration == 0 each agent initialize(agent) else each agent reacts to msgs in its context
            self.create_data(iteration) # abs method, create data relevant to algorithm type
            if self.is_terminated(): # abs method, is algorithm self terminated before max termination
                break
            msgs_to_send = self.handle_msgs()  # decrease msg delay by 1 and return map by receivers
            self.agents_receive_msgs(msgs_to_send)  # agents update their context # TO DO



    # called by execute, decrease msg delay by 1 and return map by receivers
    def handle_msgs(self):
        sorted_msgs = sorted(self.msg_box, key=Msg.comparator_by_msg_delay)
        ans = []
        for i in range(len(sorted_msgs)):
            msg = sorted_msgs[i]
            if msg.delay == 0: ans.append()
            else: msg.delay = msg.delay - 1
        self.msg_box = [i for i in self.msg_box if i.delay != 0]
        return ans




    # called by execute, if iteration == 0 each agent initialize(agent) else each agent reacts to msgs in its context
    def agents_react_to_msgs(self, iteration):
        for agent in self.agents:
            if iteration == 0: self.agents_initialize(agent)
            else: self.reaction_to_algorithmic_msgs(agent)

    def reaction_to_algorithmic_msgs(self, agent):
        self.compute(agent)
        agent.update_time_stamp()
        self.send_msgs(agent)

    def compute(self, agent):
        raise NotImplementedError()

    def send_msgs(self, agent):
        raise NotImplementedError()


    # called by execute, organize the messages in a map. the key is the receiver and the values are the msgs received
    def agents_receive_msgs(self, msgs_to_send):
        self.create_map_by_receiver(msgs_to_send)
        for key, value in  self.receives_in_current_iteration.items():
            msgs_per_agent = value
            receiver_agent = self.get_agent_by_id(key)
            if receiver_agent is None:
                print("in Mailer, agents_receive_msg did not find agent by id")
            self.an_agent_receive_msgs(receiver_agent, msgs_per_agent)


    # called by agents_receive_msgs organize the messages in a map, key = receiver agent, value = msgs list
    def create_map_by_receiver(self, msgs_to_send):
        self.receives_in_current_iteration = {}
        for msg in msgs_to_send:
            receiver = msg.receiver_id
            if receiver not in self.receives_in_current_iteration:
                self.receives_in_current_iteration[receiver] =[]
            self.receives_in_current_iteration[receiver].append(msg)

    # called by agents_receive_msgs gets
    def get_agent_by_id(self, agent_id):
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        else:
            return None




    # called from execute, abs method, agent prepares input
    def prepare_algorithm_input(self, agent):
        raise NotImplementedError()

    # called from execute,abs method, create data relevant to algorithm type
    def create_data(self, iteration):
        raise NotImplementedError()

    def agents_initialize(self, agent):
        raise NotImplementedError()

    def is_terminated(self):
        raise NotImplementedError()

    def an_agent_receive_msgs(self, receiver_agent, msgs_per_agent):
        for msg in msgs_per_agent:
            if not self.delay.is_time_stamp:
                self.agent_receive_a_single_msg(receiver_agent = receiver_agent, msg = msg)
            else:
                time_stamp_held_by_agent = self.get_current_time_stamp(receiver_agent = receiver_agent, sender_id = msg.sender_id)
                time_stamp_of_msg_to_be_sent = msg.time_stamp
                if time_stamp_held_by_agent<time_stamp_of_msg_to_be_sent:
                    self.agent_receive_a_single_msg(receiver_agent=receiver_agent, msg=msg)

    def get_current_time_stamp(self, receiver_agent, sender_id):
        raise NotImplementedError()

    def agent_receive_a_single_msg(self,receiver_agent, msg):
        raise NotImplementedError()

class MailerDistributed(Mailer):
    def __init__(self, termination, problem, delay_protocol):
        Mailer.__init__(self, termination=termination, problem=problem, delay_protocol=delay_protocol)
        self.agent_host_missions_map = {}
        self.create_agent_host_missions_map()

    def create_agent_host_missions_map(self):
        for agent in self.agents:
            self.agent_host_missions_map[agent] = agent.taskResponsibility


class MailerFisher(MailerDistributed):
    def __init__(self , termination, problem, delay_protocol, ,random_utils_parameters, random_utils_boolean = True  ):
        Mailer.__init__(self, termination=termination, problem=problem, delay_protocol=delay_protocol)
        self.random_utils_parameters = random_utils_parameters
        self.random_utils_boolean = random_utils_boolean

    def prepare_algorithm_input(self):
        for agent in self.agents:
            if self.random_utils_boolean:
                agent.create_missions_random_utils(missions=self.missions, util_parameters = self.random_utils_parameters)

    def create_data(self, iteration):
        self.results[iteration] = DataFisher(iteration, self.agents, self.missions)