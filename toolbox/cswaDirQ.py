from dirq.QueueSimple import QueueSimple
import sys
from time import sleep, time
import datetime
#from cswaUpdateCSpace import processqueueelement

queue_dir = sys.argv[1]

# sample producer

# dirq = QueueSimple(queue_dir)
# for count in range(1,101):
#    name = dirq.add("element %i\n" % count)
#    print("# added element %i as %s" % (count, name))

# sample consumer

dirq = QueueSimple(queue_dir)
passes = 0
items = 0
elapsedtime = time()
logmessageinterval = 60 #seconds
WHEN2POST = 'queue'

while True:
    for name in dirq:
        if not dirq.lock(name):
            continue
        print("# reading element %s" % name)
        data = dirq.get(name)
        print(data)
        # one could use dirq.unlock(name) to only browse the queue...
        dirq.unlock(name)
        # print("# removing element %s" % name)
        # dirq.remove(name)
        items += 1
        print("# items processed: %s" % items)
    sys.exit()
    sleep(1)
    passes += 1
    if time() - elapsedtime > logmessageinterval:
        print('pass %s, items %s, date %s' % (passes, items, datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")))
        elapsedtime = time()