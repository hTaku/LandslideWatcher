import sys
from config_test import *
from logic.logger.logger import Logger
from logic.connect_big_region import BigRegion

'''
Previos process
'''
class Preprocessing:

    # Instance of config(config_test or config_train) class
    __config = None
    __logger = None


    '''
    initialize
    '''        
    def __init__(self, __config, __logger=None):
        self.__config = __config
        self.__logger = __logger
        _exec_mode = 'product'
        self.__printLog('=============Preprocessing=================')
        self.__printLog('input      : ' + self.__config.INPUT_DIR)
        self.__printLog('output     : ' + self.__config.OUTPUT_DIR)
        self.__printLog('temp       : ' + self.__config.TEMP_DIR)
        self.__printLog('occurrence : ' + '\033[31m' + self.__config.OCCURRENCE + '\033[0m')
        if isinstance(__config, config_test):
            self.__printLog('sample file: ' + self.__config.SAMPLE_FILE)
            _exec_mode = 'test'
        self.__printLog('exec_mode  : ' + '\033[31m' + _exec_mode + '\033[0m')
        self.__printLog('=============Preprocessing=================')

    '''
    Previos processes

    1. Join patch image files 
    '''
    def run(self):
        _bigregion = BigRegion(self.__config.IMG_WIDTH, self.__config.IMG_HEIGHT, self.__logger)
        _ans_file = ''
        if isinstance(self.__config, config_test):
            _ans_file = self.__config.SAMPLE_FILE
        _bigregion.attachOccurrenceFlag(self.__config.OCCURRENCE, self.__config.INPUT_DIR, self.__config.TEMP_DIR, _ans_file)
        _bigregion.collect(self.__config.TEMP_DIR, _debug=False)
        _bigregion.create(self.__config.OUTPUT_DIR + '/' + self.__config.PREPROC_DIR_NAME, src_delete=True)


    def __printLog(self, __msg, __log_level=''):
        if self.__logger == None:
            print(__msg)
        else:
            if __log_level == 'error':
                self.__logger.error(__msg)
            else:
                self.__logger.info(__msg)


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 4:
        if (args[1] == 'test' or args[1] == 'train') and (args[2] == 'before' or args[2] == 'after') and (args[3] == 'PALSAR' or args[3] == 'LANDSAT'):
            config = config_test(args[2], args[3])
            preproc = Preprocessing(config)
            preproc.run()
            sys.exit(0)

    print('Failed argments!')
    print('e.g.) python preprocessing.py ''test/train'' ''before/after'' ''PLASAR/LANDSAT'' [delflg]')

