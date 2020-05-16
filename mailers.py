class Mailer(object):
    def __init__(self, termination, problem, delay_protocol):
        self.termination = termination
        self.agents = problem.agents
        self.missions = problem.missions
        self.delay = delay_protocol
        self.prepare_fields()
        self.msg_box = []
        self.results = {}

    def prepare_fields(self):
        for agent in self.agents:
            agent.reset()
        for mission in self.missions:
            mission.reset()
        self.delay.set_seed()

    def execute(self):
        self.prepare_algorithm_input()


        for iteration in range(1, self.termination):
            self.agents_react_to_msgs(iteration)  # agents creates computations # TO DO
            self.create_Data(iteration)
            msgs_to_send = self.handle_msgs  # decrease msg delay by 1 and return map by receivers # TO DO
            self.agents_recieve_msg(msgs_to_send)  # agents update their context # TO DO

    def prepare_algorithm_input(self):
        raise NotImplementedError()

    def agents_initialize(self):
        raise NotImplementedError()

    def agents_react_to_msgs(self, iteration):

        if iteration == 0:
            self.agents_initialize(self)
        else




class MailerDistributed(Mailer):
    def __init__(self, termination, problem, delay_protocol):
        Mailer.__init__(self, termination=termination, problem=problem, delay_protocol=delay_protocol)
        self.agent_host_missions_map = {}
        self.create_agent_host_missions_map()

    def create_agent_host_missions_map(self):
        for agent in self.agents:
            self.agent_host_missions_map[agent] = agent.taskResponsibility


class MailerFisher(MailerDistributed):
    def __init__(self, termination, problem, delay_protocol, random_utils=True):
        Mailer.__init__(self, termination=termination, problem=problem, delay_protocol=delay_protocol)
        self.random_utils = random_utils

    def prepare_algorithm_input(self):
        for agent in self.agents:
            agent.create_missions_utils(missions=self.missions, random_utils=True)
