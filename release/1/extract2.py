from coscaleds.interact import * 
import cPickle as pickle
import numpy as np

c = connect("prodmon")

start = epoch(2017, 6, 14)
stop = epoch(2017, 6, 14, 8, 20)
interval = 60

expected_points = (stop - start) / interval + 1 

metric_index = {}
for m in c.api.metric.all(c.appid, options=Options().expand('dimensions')):
    metric_index[m['id']] = m

server_metrics = c.api.server.all(c.appid, options=Options().expand("metrics"))

server_index = {}
for s in server_metrics:
    server_index[s['id']] = s
    print s['name'] 
 
target_metrics = {"Average CPU user time" : ""}
#                   "Log plugin - Workers - Number of logs" : "logs"}
 
candidates = []
for s in server_metrics:
    for m in s['metrics']:
        if m['id'] in metric_index and m['name'] in target_metrics:
            if ("memory" not in m['name']) and metric_index[m['id']]['dimensions'] == []:
                candidates.append((s['id'], m['id']))
 
print "Found %d candidates" % len(candidates)
 
data = []
names = []
 
RBX = ".prod-rbx1.coscale.com"
CPU = "cpu"
 
def nice_server_name(sname):
    if sname.endswith(RBX):
        return server['name'][:len(server['name']) - len(RBX)]
    elif sname.startswith(CPU):
        return "host" + server['name'][len(CPU):]
    else:
        return sname
 
for server_id, metric_id in np.random.permutation(candidates):
    server = server_index[server_id]
    metric = metric_index[metric_id]
     
    print "\t\tGetting data for metric %s and server %s" % (metric['name'], server['name'])
    received = c.data.get(metric_id, "s%d" % server_id, start, stop, interval, "AVG")
    values = received['values']
    if len(values) > 0:
        timeseries = np.array(values)[:, 1]        
        if len(timeseries) != expected_points:
            print "EXPECT"
        elif np.any(np.isnan(timeseries)):
            print "NANS"
        elif np.mean(timeseries) <= 0:
            print "MEAN"
        elif (np.max(timeseries) - np.min(timeseries)) / np.mean(timeseries) < 0.05:
            print "NOVAR"
        else:
            data.append(list(timeseries))
             
            if server['name'].endswith(RBX):
                short_name = server['name'][:len(server['name']) - len(RBX)]
            elif server['name'].startswith(CPU):
                short_name = "host" + server['name'][len(CPU):] 
             
            names.append("%s%s" % (nice_server_name(server['name']), target_metrics[metric['name']]))
            print "[%d] ==========> Got %d points for %s " % (len(data), len(timeseries), names[-1])
    else:
        print "No data found"
 
data = np.array(data, dtype=np.float)
names = np.array(names, dtype=object)
 
with open("data/correlation_series_cpu.pickle", 'wb') as f:
    pickle.dump((names, data), f)
     
print "Data was written"