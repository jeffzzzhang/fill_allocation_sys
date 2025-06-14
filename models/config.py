import yaml

CONFIG_DIR = "config/"
CONFIG_FILE_NAME = "app_config.yaml"


def get_config():
    with open(CONFIG_DIR+CONFIG_FILE_NAME, "r") as file:
        config = yaml.safe_load(file)
    return config
