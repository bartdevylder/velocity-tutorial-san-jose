from coscaleds.interact import * 
import cPickle as pickle
import numpy as np

c = connect("prodmon")

metric_index = {}
server_index = {}

for m in c.api.metric.all(c.appid):
    metric_index[m['name']] = m

for s in c.api.server.all(c.appid):
    server_index[s['name']] = s

start = epoch(2017, 6, 12)
stop = epoch(2017, 6, 13)
interval = 300

data_to_fetch = [("rumdatareceiver_log_lines", "Log plugin - number of log entries", "rumdatareceiver002.prod-rbx1.coscale.com"),
                 ("pageminer_loglines",        "Log plugin - Workers - Number of logs", "pageminer002.prod-rbx1.coscale.com"),
                 ("rumaggregator_loglines",    "Log plugin - Workers - Number of logs", "rumaggregator002.prod-rbx1.coscale.com"),
                 ("reporter_loglines",         "Log plugin - Workers - Number of logs", "reporter002.prod-rbx1.coscale.com")]

names = []
data = []

for target_name, metric_name, server_name in data_to_fetch:
    metric_id = metric_index[metric_name]['id']
    server_id = server_index[server_name]['id']

    print "Getting data for metric %d and server %d" % (metric_id, server_id)
    received = c.data.get(metric_id, "s%d" % server_id, start, stop, interval, "AVG")
    data.append(np.array(received['values'])[:, 1])
    names.append(target_name)
    print "Got %d points" % len(data[-1])


data = np.array(data, dtype=np.float)
names = np.array(names, dtype=object)

with open("data/correlation_series.pickle", 'wb') as f:
    pickle.dump((names, data), f)
    
print "Data was written"