from config_common import config_common

class config_train(config_common):

    NEGATIVE = 'negative'

    POSITIVE = 'positive'

    def __init__(self, __occurrence, __satname):
        _super = super().__init__('train', __occurrence, __satname)
        self.IMG_WIDTH = 40
        self.IMG_HEIGHT = 40
        self.INPUT_DIR = self.INPUT_DIR + '/*'


