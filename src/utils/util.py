import os
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

