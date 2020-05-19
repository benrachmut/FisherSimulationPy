class Msg(object):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.context = context
        self.time_stamp = time_stamp
        self.delay = None


    @staticmethod
    def comparator_by_msg_delay(msg):
        return msg.delay


class MsgFisher(Msg):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        Msg.__init__(self, sender_id, receiver_id, context, time_stamp)


class MsgBid(MsgFisher):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)


class MsgAllocation(MsgFisher):
    def __init__(self, sender_id, receiver_id, context, time_stamp):
        MsgFisher.__init__(self, sender_id, receiver_id, context, time_stamp)
