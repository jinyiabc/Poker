import os

from poker.tools.helper import get_dir, get_config, get_multiprocessing_config
from configobj import ConfigObj
from PIL import Image

if __name__ == '__main__':

    print(get_dir('tools'))
    print(get_dir('tests', 'screenshots'))
    entire_screen_pil = Image.open(os.path.join(get_dir('tests', 'screenshots'), 'test2.png'))
    # print(get_config())
    config = get_config()
    print(config.sections())
    print(config['MulitiProcessing']['cores'])
    print(config['DEFAULT']['montecarlo_timeout'])
    config = get_config()
    parallel = config.getboolean('MulitiProcessing', 'parallel')
    cores = config.getint('MulitiProcessing', 'cores')
    print(parallel)
    print(cores)

    config = ConfigObj('config.ini')
    config.filename = 'test.ini'
    config.write()
    print(config == ConfigObj('test.ini', raise_errors=True))   # True



