from collectory import config

DEFAULT_FILE = "default_collection"

def default_path():
    return config.collection_path(DEFAULT_FILE)