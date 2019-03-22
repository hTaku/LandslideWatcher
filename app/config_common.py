
class config_common(object):
    # Preprocessing directory name
    PREPROC_DIR_NAME = '1_pre'

    # Leaning directory name
    LEANING_DIR_NAME = '2_leaning'

    # Predicting directory name
    PREDICTING_DIR_NAME = '3_predicting'

    # input data directory
    INPUT_DIR = '../data/input'

    # output data directory
    OUTPUT_DIR = '../data/output'

    # temp directory
    TEMP_DIR = '../data/tmp'

    # Preprocessing directory
    PRE_DIR = str()

    # Occurrence Flag
    OCCURRENCE = str()

    # Image width
    IMG_WIDTH = 10

    # Image height
    IMG_HEIGHT = 10

    # log directory
    LOG_DIR = '../log'

    # log output(stream/file/both)
    LOG_OUTPUT = 'both'

    # log filename
    LOG_FILENAME = 'app.log'

    # log level
    LOG_LEVEL = 'debug'

    # log format
    LOG_FORMAT = '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'

    def __init__(self, __proc_type, __occurrence, __satname):
        _subdir = '/' + __proc_type + '/' + __satname + '/' + __occurrence

        self.OCCURRENCE = __occurrence
    
        self.INPUT_DIR  = self.INPUT_DIR + _subdir
        self.OUTPUT_DIR = self.OUTPUT_DIR + _subdir
        self.PRE_DIR    = self.INPUT_DIR + '/' +  self.PREPROC_DIR_NAME
