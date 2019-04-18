from environs import Env, EnvError
import logging

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('canadadata')
logger.setLevel(logging.DEBUG)

_env = Env()
_env.read_env()

try:
    CACHE_DIR = _env('cache_dir')
    logger.info(f'Property "cache_dir" set to {CACHE_DIR}')
except EnvError:
    logger.error('Property "cache_dir" not set in .env file')
    CACHE_DIR = '.'



