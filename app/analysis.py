import sys

from config_test import *
from config_train import *
from preprocessing import Preprocessing
from logic.logger.logger import Logger


class analysis:
    __logger = None
    
    def __init__(self):
        pass


    '''
    Run test scenario.
    '''
    def test_scenario(self):
        _config_before = config_test('before', 'PALSAR')
        _config_after = config_test('after', 'PALSAR')

        _log_file = _config_before.LOG_DIR + '/' + _config_before.LOG_FILENAME
        self.__logger = Logger('LandslideWatcher', _config_before.LOG_OUTPUT, _log_file, _config_before.LOG_LEVEL, _config_before.LOG_FORMAT)
        
        # 1. Previos Process(before)
        _preprc_before = Preprocessing(_config_before, self.__logger)
        _preprc_before.run()
        # 2. Previos Process(after)
        _preprc_after = Preprocessing(_config_after, self.__logger)
        _preprc_after.run()

    '''
    Run product scenario.
    '''
    def product_scenario(self):
        _config_before = config_train('before', 'PALSAR')

        _log_file = _config_before.LOG_DIR + '/' + _config_before.LOG_FILENAME
        self.__logger = Logger('LandslideWatcher', _config_before.LOG_OUTPUT, _log_file, _config_before.LOG_LEVEL, _config_before.LOG_FORMAT)
        
        _preprc_before = Preprocessing(_config_before, self.__logger)
        _preprc_before.run()

        _config_after = config_train('after', 'PALSAR')
        _preprc_after = Preprocessing(_config_after, self.__logger)
        _preprc_after.run()


if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        print('Failed argument is shortest!!')
        print('e,.g.) python analysis.py ''test/product''')
        sys.exit(1)
    else:
        if args[1] != 'test' and args[1] != 'product':
            print('Illegal argument!!')
            print('e,.g.) python analysis.py ''test/product''')
            sys.exit(1)

    proc = analysis()
    if args[1] == 'test':
        proc.test_scenario()
    elif args[1] == 'product':
        proc.product_scenario()

