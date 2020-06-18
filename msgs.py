class Msg(object):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.context = context
        self.time_stamp = time_stamp
        self.delay = None

    def __str__(self):
        return "sender",self.sender_id,"receiver",self.receiver_id,self.str_specific()

    @staticmethod
    def comparator_by_msg_delay(msg):
        return msg.delay

    def str_specific(self):
        raise NotImplementedError()


class MsgFisher(Msg):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        Msg.__init__(self, sender_id, receiver_id, context, time_stamp)


# From agent to mission
class MsgFisherBid(MsgFisher):
    def __init__(self, sender_id, context, time_stamp, mission_receiver_id, receiver_id=None):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
        self.mission_receiver_id = mission_receiver_id

    def str_specific(self):
        return "bid", self.context


# From mission to agent
class MsgFisherAllocation(MsgFisher):
    def __init__(self, sender_id, receiver_id, context, time_stamp, mission_sender_id):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
        self.mission_sender_id = mission_sender_id

        def str_specific(self):
            return "allocation", self.context


class MsgFisherMissionConverge(MsgFisher):
    def __init__(self, sender_id, receiver_id, context, time_stamp, mission_sender_id):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
        self.mission_sender_id = mission_sender_id

        def str_specific(self):
            return "mission_converge"
