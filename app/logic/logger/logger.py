import logging
from logging import *

class Logger:
    __logger = None

    def __init__(self, log_name, output_stream='both', filename='', log_level='NOTSET', log_format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'):
        level = self.__getLogLevel(log_level)

        self.__logger = getLogger(log_name)
        self.__logger.setLevel(level)

        handler_format = Formatter(log_format)

        if output_stream == 'stream':
            self.__output_stream(level, handler_format)
        elif output_stream == 'file':
            self.__output_file(filename, level, handler_format)
        elif output_stream == 'both':
            self.__output_stream(level, handler_format)
            self.__output_file(filename, level, handler_format)
        else:
            raise AttributeError('argument[output_stream] is substitution "stream/file/both".')


    def critical(self, msg):
        self.__logger.critical(msg)
    
    def error(self, msg):
        self.__logger.error(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def info(self, msg):
        self.__logger.info(msg)

    def debug(self, msg):
        self.__logger.debug(msg)

    def print(self, msg):
        self.__logger.notset(msg)


    def __output_stream(self, level, handler_format):
        stream_handler = StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(handler_format)

        self.__logger.addHandler(stream_handler)


    def __output_file(self, filename, level, handler_format):
        if filename == '':
            raise AttributeError('argument[filename] is mast designation.')
        file_handler = FileHandler(filename, 'a')
        file_handler.setLevel(level)
        file_handler.setFormatter(handler_format)

        self.__logger.addHandler(file_handler)
       

    def __getLogLevel(self, log_level):
        result = logging.NOTSET
        log_level = log_level.upper()
        if log_level == 'CRITICAL':
            result = logging.CRITICAL
        elif log_level == 'ERROR':
            result = logging.ERROR
        elif log_level == 'WARNING':
            result = logging.WARNING
        elif log_level == 'INFO':
            result = logging.INFO
        elif log_level == 'DEBUG':
            result = logging.DEBUG
        else:
            result = NOTSET
        return result


    


