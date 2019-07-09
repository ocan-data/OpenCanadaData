from ruamel.yaml import YAML
import sys

if __name__ == '__main__':
    yaml = YAML(typ='safe')
    env_file = sys.argv[1]
    with open(env_file, 'r') as f:
        conf = yaml.load(f)
        print(conf['name'])