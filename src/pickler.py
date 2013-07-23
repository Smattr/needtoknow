import pickle

def save(filename, obj):
    with open(filename, 'w') as f:
        pickle.dump(obj, f)

def restore(filename):
    with open(filename, 'r') as f:
        return pickle.load(f)
