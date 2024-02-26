import json
import os

def get_database_settings():
    file_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(file_path) as config_file:
        config = json.load(config_file)
        postgres_config = config["postgres"]
        return postgres_config