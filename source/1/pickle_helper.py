import pickle
import sys

def load(name):
    if sys.version_info[0] < 3:
        return pickle.load(open(name))
    else:
        return pickle.load(open(name, 'rb'), encoding='latin1')    