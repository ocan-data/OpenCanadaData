from environs import Env
import logging

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('ocandata')
logger.setLevel(logging.DEBUG)

env = Env()
env.read_env()

CACHE_DIR = env('cache_dir', '.')
DOTPATH = env('DOTPATH', 'canadadata')



