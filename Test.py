from msgs import Msg

ans = {}
ans["a"]=1
ans["b"]=2
ans["c"]=3

print(str(abs(-3)))
print("is a in ans "+str("n" in ans))
for key, value in ans.items():
    print(key)
    print(value)


receiver = 4
print("is receiver in ans"+str(receiver not in ans))

m1  = Msg(sender_id = 3, receiver_id=4, context=5, time_stamp=2)
m1.delay = 0
m2  = Msg(sender_id = 3, receiver_id=4, context=5, time_stamp=2)
m2.delay = 3
m3  = Msg(sender_id = 3, receiver_id=4, context=5, time_stamp=2)
m3.delay = 2

msgs = [m1,m2,m3]

sorted_msgs = sorted(msgs, key=Msg.comparator_by_msg_delay)

print(3)

msgs_new = [i for i in msgs if i.delay ==0]


ll= [i for i in l if i % 2 == 0]
print(ll)

print([i for i in l if i % 2 != 0])

print(l)
