from abc import ABC
from numpy import mean

from msgs import Msg
from problem_entities import Agent


class DataPerIteration(object):
    def __init__(self, iteration, agents, missions, previous_data=None):
        self.iteration = iteration
        self.agents = agents
        self.missions = missions

        self.rx_bird_eye_matrix, self.rx_bird_eye_sum, self.x_matrix, self.bids_mission_pov, self.r_matrix, self.rx_per_agent_map = self.create_rx_bird_eye()
        self.rx_agent_view_sum, self.rx_agent_view_sum, self.bids_agents_pov = self.create_rx_agent_view()
        self.util_if_change_bird_eye_matrix, self.envy_bird_eye_max, self.envy_score_bird_eye_matrix = self.create_envy_score()

        self.price_map = self.get_prices()
        if iteration > 0:
            self.mono_per_agent_rx_weakly, self.mono_global_rx_weakly = self.check_mono(previous_data=previous_data,
                                                                            weakly=True)
            self.delta_abs_price_per_mission,self.delta_abs_price,self.delta_non_abs_price_per_mission,self.delta_non_abs_price = self.get_delta_price(previous_data)

    def get_delta_price(self, previous_data):
        previous_price_map = previous_data.price_map
        delta_map_abs = {}
        delta_map_non_abs = {}
        for mission_id, previous_price in previous_price_map.items():
            delta_map_non_abs[mission_id] = previous_price - self.price_map[mission_id]
            delta_map_abs[mission_id] = abs(previous_price - self.price_map[mission_id])
        return delta_map_abs, sum(delta_map_abs.values()),delta_map_non_abs,sum(delta_map_non_abs.values())

    def check_mono(self, previous_data, weakly):
        previous_rx_per_agent = previous_data.rx_per_agent_map
        mono_per_agent = {}
        for agent_id, previous_rx_i in previous_rx_per_agent.items():
            current_rx_i = self.rx_per_agent_map[agent_id]
            if weakly:
                if current_rx_i >= previous_rx_i:
                    monotonic_score_per_agent = 1
                else:
                    monotonic_score_per_agent = 0
            else:
                if current_rx_i > previous_rx_i:
                    monotonic_score_per_agent = 1
                else:
                    monotonic_score_per_agent = 0

            mono_per_agent[agent_id] = monotonic_score_per_agent


        previous_rx_sum = previous_data.rx_bird_eye_sum
        if weakly:
            if previous_rx_sum <= self.rx_bird_eye_sum:
                overall_mono = 1
            else:
                overall_mono = 0
        else:
            if previous_rx_sum < self.rx_bird_eye_sum:
                overall_mono = 1
            else:
                overall_mono = 0

        #vvv=[]
        #for v in mono_per_agent.values():
        #    vvv.append(v)
        #is_overall_mono = mean(vvv)
        #if is_overall_mono == 1:
        #    overall_mono = 1
        #else:
        #    overall_mono = 0
        return mono_per_agent, overall_mono

    def get_prices(self):
        ans = {}
        for mission in self.missions:
            ans[mission.mission_id] = mission.price
        return ans

    def create_envy_score(self):
        util_if_can_change = self.get_util_if_can_change()
        envy_score, envy_matrix = self.get_matrix_envy_score(util_if_can_change)
        return util_if_can_change, envy_score, envy_matrix

    def get_matrix_envy_score(self, input_m):
        ans = []
        max_vector = []
        for i in range(len(input_m)):
            i_vector = input_m[i]
            i_util = i_vector[i]
            i_envy_score = []
            for j in range(len(input_m)):
                j_util = i_vector[j]
                util = 0
                if i_util < j_util:
                    util = j_util - i_util
                i_envy_score.append(util)
            max_vector.append(max(i_envy_score))
            ans.append(i_envy_score)

        score = max(max_vector)
        return score, ans

    def get_util_if_can_change(self):
        ans = []
        for i in range(len(self.agents)):
            agent_i = self.get_agent_given_id(i)
            r_i = agent_i.r_i
            util_if_can_change_agent_i = []
            for k in range(len(self.agents)):
                x_k = self.get_bird_eye_x_per_agent(k)
                temp_util = 0
                for mission_id, r_ij in r_i.items():
                    temp_util = temp_util + r_ij.get_utility(x_k[mission_id])
                util_if_can_change_agent_i.append(temp_util)
            ans.append(util_if_can_change_agent_i)
        return ans

    def get_bird_eye_x_per_agent(self, k):
        ans = {}
        for mission in self.missions:
            ans[mission.mission_id] = mission.allocation_placed_for_agents[k]
        return ans

    def get_agent_given_id(self, i):
        for agent in self.agents:
            if agent.agent_id == i:
                return agent
        print("cant find agent in data")

    def create_rx_agent_view(self):
        matrix_sum = 0
        matrix = []
        bids_agents_pov = []
        for agent in self.agents:
            rx_i = []
            agent_id = agent.agent_id
            bids_per_agent = []

            for mission_id, bid in agent.bid_placed_for_missions.items():
                bids_per_agent.append(agent.bid_placed_for_missions[mission_id])
            bids_agents_pov.append(bids_per_agent)

            for mission_id, x_ij_agent_view in agent.x_i.items():
                mission = self.get_mission_given_id(mission_id)
                x_ij = mission.allocation_placed_for_agents.get(agent_id)
                r_ij = agent.r_i[mission_id]
                matrix_sum = matrix_sum + r_ij.get_utility(x_ij)
                rx_i.append(r_ij.get_utility(x_ij))
                agent.bid_placed_for_missions[mission_id]

        return matrix, matrix_sum,bids_agents_pov

    def create_rx_bird_eye(self):
        r_global = []
        x_global = []
        matrix = []
        bids = []
        matrix_sum = 0

        rx_per_agent_map = {}
        for agent in self.agents:
            rx_i = []
            x_i = []
            bids_i = []
            agent_id = agent.agent_id
            r_i = agent.r_i
            r_i_list = []

            sum_per_agent = 0
            for mission_id, r_ij in r_i.items():
                mission = self.get_mission_given_id(mission_id)
                x_ij = mission.allocation_placed_for_agents.get(agent_id)
                bid_ij = mission.bids[agent_id]
                r_i_list.append(r_ij)
                matrix_sum = matrix_sum + r_ij.get_utility(x_ij)
                sum_per_agent = sum_per_agent + r_ij.get_utility(x_ij)
                rx_i.append(r_ij.get_utility(x_ij))
                x_i.append(x_ij)
                bids_i.append(bid_ij)

            rx_per_agent_map[agent] = sum_per_agent
            r_global.append(r_i_list)
            bids.append(bids_i)
            matrix.append(rx_i)
            x_global.append(x_i)

        return matrix, matrix_sum, x_global, bids, r_global, rx_per_agent_map

    def get_mission_given_id(self, mission_id):
        for mission in self.missions:
            if mission.mission_id == mission_id:
                return mission
        print("in data cannot find mission id")




class Mailer(object):
    def __init__(self, problem_id, agents, missions, delay_protocol, termination, debug_print_problem, is_random,
                 is_include_data):
        self.is_include_data = is_include_data
        self.problem_id = problem_id
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
        self.delays = []
        self.debug_print_problem = debug_print_problem

    # called from agent to send msg

    def send_msg_no_delay(self, msg):
        msg.delay = 0
        self.msg_box.append(msg)

    def send_msg(self, msg):
        delay = self.delay.create_delay()
        if delay is None or delay < 0:
            delay = 0
        self.delays.append(delay)
        msg.delay = delay
        self.msg_box.append(msg)

    def execute(self):
        for agent in self.agents:
            agent.meet_mailer(self)
        self.prepare_fields()
        self.execute_specific()

    def execute_specific(self):
        raise NotImplementedError()

    def create_agent_host_missions_map(self):
        for agent in self.agents:
            self.agent_host_missions_map[agent] = agent.get_mission_responsibility_ids()

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

        self.agent_host_missions_map = {}
        self.create_agent_host_missions_map()
        for agent in self.agents:
            agent.inform_agent_host_missions_map(map_input=self.agent_host_missions_map)
        self.delay.set_seed(self.problem_id)

    # 1.2 called from execute,abs method, create data relevant to algorithm type
    def create_data(self, time, debug_print_problem, previous_data):
        data = DataPerIteration(iteration=time, agents=self.agents, missions=self.missions, previous_data = previous_data)

        if time >= 1:
            self.results[time] = data

        if debug_print_problem:
            print()
            print("--------------------iteration:",time-1,"--------------------")
            print()
            if time%2 == 0:
                print("bids agent pov matrix:")
                self.print_2D(data.bids_agents_pov)
                print()
                if time > 0:
                    print("delta abs price:")
                    print(data.delta_abs_price)
                    print("delta abs price per mission:")
                    print(data.delta_abs_price_per_mission)
                    print()
                    print("delta non_abs price:")
                    print(data.delta_non_abs_price)
                    print()
            else:
                print("X matrix:")
                self.print_2D(data.x_matrix)
                print()
                print("RX bird eye matrix:")
                self.print_2D(data.rx_bird_eye_matrix)
                print()
                print("RX sum:")
                print(data.rx_bird_eye_sum)
                print()
                print("Envy Matrix if change x with others:")
                self.print_2D(data.util_if_change_bird_eye_matrix)
                print()
                print("Envy Matrix Score")
                self.print_2D(data.envy_score_bird_eye_matrix)
                print()
                print("Max Envy")
                print(data.envy_bird_eye_max)

        return data

    def print_2D(self, matrix):
        for v in matrix:
            print(v)




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
                receiver_agent.agent_receive_a_single_msg(msg=msg)
            else:
                time_stamp_held_by_agent = receiver_agent.get_current_time_stamp(msg)
                time_stamp_of_msg_to_be_sent = msg.time_stamp
                if time_stamp_held_by_agent < time_stamp_of_msg_to_be_sent:
                    receiver_agent.agent_receive_a_single_msg(msg=msg)




# ------------

class MailerIterations(Mailer):
    def __init__(self, problem_id, agents, missions, delay_protocol, termination, debug_print_problem, is_random,
                 is_include_data):
        Mailer.__init__(self, problem_id, agents, missions, delay_protocol, termination, debug_print_problem, is_random,
                        is_include_data)

    # ---------
    # 1. initiate the simulator
    def execute_specific(self):
        for iteration in range(-1, self.termination):
            self.agents_react_to_msgs(iteration)
            if iteration == 0:
                previous_data = self.create_data(time=iteration, debug_print_problem=self.debug_print_problem, previous_data=None)
            if iteration > 0:
                previous_data = self.create_data(time=iteration, debug_print_problem=self.debug_print_problem, previous_data=previous_data)
            if self.is_terminated():
                break
            msgs_to_send = self.handle_msgs()
            self.agents_receive_msgs(msgs_to_send)
        print("finish run")

    def is_terminated(self):
        for agent in self.agents:
            if agent.is_fisher_phase_I:
                return False
        return True

    def agents_react_to_msgs(self, iteration):
        for agent in self.agents:
            if iteration == -1:
                agent.initialize()
            else:
                agent.compute()
            agent.msg_time_stamp = agent.msg_time_stamp + 1
            agent.send_msgs()

    # 1.5 called by execute, decrease msg delay by 1 and return map by receivers, returns msgs with no delay
    def handle_msgs(self):
        sorted_msgs = sorted(self.msg_box, key=Msg.comparator_by_msg_delay)
        ans = []
        for i in range(len(sorted_msgs)):
            msg = sorted_msgs[i]
            if msg.delay <= 0:
                ans.append(msg)
            else:
                msg.delay = msg.delay - 1
        self.msg_box = [i for i in self.msg_box if i.delay >= 0]
        return ans

    # ---------
