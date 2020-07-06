import random

# -----------------**Protocols**---------------

'''
represents a single permuataion of paramaters used to ignitiate a random delay
ProtocolDelay was written originally as an abstract class, includes three fields relevant to all CreatorDelays:
perfect communication: if true = no delay and all fields are getting defulat parameters (taken care of the class below in this script: CreatorDelays
is_time_stamp: determines if agents use \ ignore message time stamp
gammas: probability of a sent message to be lost

needs to be extended by your chosen  delay protocol
NotImplementedError raised by: create_delay_specific (returns delay using parameters) and set_seed_sepcific (sets seed to random fields)


CreatorDelays was written originally as an abstract class, includes two fields relevant to all CreatorDelays:
'''


class ProtocolDelay(object):
    def __init__(self, perfect_communication=True, is_time_stamp=False, gamma=0):
        self.perfect_communication = perfect_communication
        self.is_time_stamp = is_time_stamp
        self.gamma = gamma
        self.gamma_counter = 0

    def create_delay_specific(self, distance_ij ):
        raise NotImplementedError()

    def create_delay(self, distance_ij=1):

        self.gamma_counter = self.gamma_counter + 100
        random.seed(self.gamma_counter * 10)
        rnd = random.random()
        if rnd < self.gamma:
            return None
        else:
            self.create_delay_specific(distance_ij = distance_ij)

    def set_seed_specific(self, seed):
        raise NotImplementedError()

    def set_seed(self, seed):
        self.gamma_counter = seed * 123
        self.set_seed_specific(seed)

    def __str__(self):
        return str(self.perfect_communication) + "," + str(self.is_time_stamp) + "," + str(self.gamma)


class ProtocolDelayEl(ProtocolDelay):
    def __init__(self, is_time_stamp=False, gamma=0, sigma=0, mu_min=0,
                 n1=0, n2=0, n3=0, n4=0, p1=0, p2=0, p3=0):
        ProtocolDelay.__init__(self, perfect_communication=True, is_time_stamp=is_time_stamp, gamma=gamma)

        self.mu_min = mu_min
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.sigma = sigma

        self.rnd_normal_counter = 0
        self.rnd_noise_counter = 0

    def set_seed_specific(self, seed):

        self.rnd_normal_counter = seed * 321
        self.rnd_noise_counter = seed * 365

    def calc_noise(self):
        self.rnd_noise_counter = self.rnd_noise_counter + 21
        random.seed(self.rnd_noise_counter * 34)
        rnd = random.random()

        prob1 = self.p1
        prob2 = prob1 + self.p2
        prob3 = prob2 + self.p3
        if rnd < prob1:
            return self.n1
        if prob1 <= rnd < prob2:
            return self.n2
        if prob2 <= rnd < prob3:
            return self.n3
        else:
            return self.n4

    def create_delay_specific(self, distance_ij):
        noise = self.calc_noise()
        mu = self.mu_min + noise * distance_ij

        self.rnd_normal_counter = self.rnd_noise_counter + 456
        random.seed(self.rnd_normal_counter * 34)
        return random.gauss(mu=mu, sigma=self.sigma)

    def __str__(self):
        super.__str__() + "," + str(self.gamma) + "," + str(self.mu_min) + "," + str(self.n1) + "," + str(
            self.n2) + "," + str(self.n3) + "," + str(self.n4) + "," + str(self.p1) + "," + str(self.p2) + "," + str(
            self.p3)


# -----------------**CREATOR DELAYS**---------------
'''
Creates combinations of different delay protocols
CreatorDelays was written originally as an abstract class, includes two fields relevant to all CreatorDelays:
perfectCommunications: if false =  all other fields will be set to defult values
is_time_stamps: determines if agents use \ ignore message time stamp
gammas: probability of a sent message to be lost

needs to be extended by your chosen creator delay protocol
NotImplementedError raised by: create_default_protocol and create_combination_delay

'''


class CreatorDelays(object):
    def __init__(self, perfect_communications, is_time_stamps, gammas):
        self.perfect_communications = perfect_communications
        self.is_time_stamps = is_time_stamps
        self.gammas = gammas

    def create_protocol_delay(self):
        ans = []
        for perfectC in self.perfect_communications:
            if perfectC == True:
                ans.append(self.create_default_protocol())
            else:
                for time_stamp in self.is_time_stamps:
                    for gamma in self.gammas:
                        combination_list = self.create_combination_delay(time_stamp, gamma)
                        for comb in combination_list:
                            ans.append(comb)
        return ans

    def create_default_protocol(self):
        raise NotImplementedError()

    def create_combination_delay(self, time_stamp, gamma):
        raise NotImplementedError()

    @staticmethod
    def header():
        return "Perfect Communication,Time Stamp Use"


class CreatorDelaysEl(CreatorDelays):
    def __init__(self, perfect_communications=[True], is_time_stamps=[True, False], gammas=[0.02], mu_mins=[10],
                 sigmas=[10], n1=0, n2=0, n3=0, n4=0, p1=1, p2=0, p3=0):
        CreatorDelays.__init__(self, perfect_communications, is_time_stamps, gammas)
        self.mu_mins = mu_mins
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.sigmas = sigmas

    def create_default_protocol(self):
        return ProtocolDelayEl()

    def create_combination_delay(self, time_stamp, gamma):
        ans = []
        for mu_min in self.mu_mins:
            for sigma in self.sigmas:
                ans.append(
                    ProtocolDelayEl(time_stamp, gamma, mu_min, sigma, self.n1, self.n2, self.n3, self.n4, self.p1,
                                    self.p2, self.p3))
        return ans

    @staticmethod
    def header():
        return CreatorDelays.header() + ",Gamma,Sigma,Mu_min,n1,n2,n3,n4,p1,p2,p3"
