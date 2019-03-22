import os
import sys
import itertools
from pathlib import Path
from utils.images.tiff import *

class preprocessing:
    mode = str()
    __dect_ansor = {}
    
    def __init__(self, _mode):
        self.mode = _mode

    def readAnsorFile(self):
        with open('../resources/input/sample_submit.tsv', 'r') as rfp:
            i = 1
            for line in rfp:
                name_value = line.split()
                self.__dect_ansor[name_value[0]] = name_value[1]
                i = i + 1

    def create_prefix_image(self):
        gen_input_path = Path('../resources/input/test/PALSAR/' + self.mode + '/').glob('*.tif')
#        gen_input_path = Path('../resources/input/test/PALSAR/' + self.mode + '/').glob('test_0000_0_2.tif')

        total_size = len(list(Path('../resources/input/test/PALSAR/' + self.mode + '/').glob('*.tif')))

        i = 1
        for img_path in gen_input_path:
            img = tiff()
            with open(img_path, 'rb') as rfp:
                imgdata = rfp.read()
                img.parse(imgdata)

                before_size = img.ifd_list.index(0).size()

                _byteorder = img.header.byteorder
                _tag = tag(img.header, int(500).to_bytes(2, _byteorder))
                _datatype = datatype(img.header, int(3).to_bytes(2, _byteorder))
                _count = bytearray(int(1).to_bytes(4, _byteorder))
                _data = 0
                if self.mode == 'after':
                    basename = os.path.basename(img_path)
                    if basename in self.__dect_ansor:
                        _data = self.__dect_ansor[basename]
                _datapointer = bytearray(int(_data).to_bytes(4, _byteorder))
                _ext_data = ifd_entry(img.header).create(_tag, _datatype, _count, _datapointer)

                img.addIFDEntry(0, _ext_data)

            with open(Path('../resources/output/1_pre/' + self.mode + '/' + img_path.name), 'wb') as wfp:
                wfp.write(img.bytedata)

            if i%1000 == 0:
                sys.stdout.write(format((i/total_size)*100, '3.1f') + '%:' + str(i) + '/' + str(total_size) + '[' + str(img_path) + ']')
                print(' .......... done     [IFD size]:' + str(before_size) + '->' + str(img.ifd_list.index(0).size()) + ': add tag{500}' + str(img.ifd_list.index(0).searchTag(500).data_pointer))
            i = i + 1

        print('finish!!!')

if __name__ == '__main__':
    before = preprocessing('before')
    before.create_prefix_image()

    after = preprocessing('after')
    after.readAnsorFile()
    after.create_prefix_image()

