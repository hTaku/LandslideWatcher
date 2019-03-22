from config_common import config_common

class config_test(config_common):

    # sample file path
    # This file is enable each PRODUCT_TYPE is 'test'
    SAMPLE_FILE = str()

    def __init__(self, __occurrence, __satname):
        _super = super().__init__('test', __occurrence, __satname)
        self.SAMPLE_FILE = self.INPUT_DIR + '/../sample_submit.tsv'
        self.IMG_WIDTH  = 40
        self.IMG_HEIGHT = 40
    
    


