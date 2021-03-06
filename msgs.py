class Msg(object):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.context = context
        self.time_stamp = time_stamp
        self.delay = None

    def __str__(self):
        return "sender",str(self.sender_id),"receiver", str(self.receiver_id),"delay",str(self.delay),"timestamp",str(self.time_stamp), \
               self.str_specific()

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
    def __init__(self, sender_id, context, time_stamp, mission_receiver_id,sender_is_phase_I, receiver_id=None):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
        self.mission_receiver_id = mission_receiver_id
        self.sender_is_phase_I = sender_is_phase_I

    def str_specific(self):
        return "bid", str(self.context),"mission_receiver_id",str(self.mission_receiver_id)


# From mission to agent
class MsgFisherAllocation(MsgFisher):
    def __init__(self, sender_id, receiver_id, context, time_stamp, mission_sender_id, mission_converge):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
        self.mission_sender_id = mission_sender_id
        self.mission_converge = mission_converge

    def str_specific(self):
        return "allocation", self.context, "mission_sender_id",str(self.mission_sender_id)


class MsgFisherMissionConverge(MsgFisher):
    def __init__(self, sender_id, receiver_id, context, time_stamp, mission_sender_id):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
        self.mission_sender_id = mission_sender_id

        def str_specific(self):
            return "mission_converge"
