import os
def localpath(path):
    return os.path.join(os.path.dirname(__file__), path)