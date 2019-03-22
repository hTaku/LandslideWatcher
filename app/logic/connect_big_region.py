import os
import sys
import itertools
from pathlib import Path
from utils.images.tiff import *
from utils.lang import byte_util as butil

class TiffInfo:
    path = str()
    tif = None

    def __init__(self, _path):
        self.path = _path
        self.tif = tiff()
        with open(_path, 'rb') as rfp:
            self.tif.parse(rfp.read())

    

class BigRegion:
    __map_group = {}
    __IMG_WIDTH  = 10
    __IMG_HEIGHT = 10
    __total_size = 0
    
    def __init__(self, __patch_img_width, __patch_img_height):
        self.__IMG_WIDTH  = __patch_img_width
        self.__IMG_HEIGHT = __patch_img_height


    '''
    Attach Occurrence Flag
    '''
    def attachOccurrenceFlag(self, _mode, _input_path, _output_path, _ans_filename = ''):
        print('[1/3] Attach Occurrence Flag.')
        print(_input_path + '/*.tif')
        self.__total_size = len(list(Path().glob(_input_path + '/*.tif')))
        if self.__total_size == 0:
            raise FileNotFoundError('Tiff file not found. [' + _input_path + '/*.tif]')
        _gen_input_path = Path().glob(_input_path + '/*.tif')
        if _ans_filename == '':
            self.__attachOccurrenceFlag_Train(_mode, _gen_input_path, _output_path)
        else:
            self.__attachOccurrenceFlag_Test(_mode, _gen_input_path, _output_path, _ans_filename)


    '''
    Attach Occurrence Flag(For train)
    '''
    def __attachOccurrenceFlag_Train(self, _mode, _gen_input_path, _output_path):
        _pi = 1
        for _img_path in _gen_input_path:
            # get directory level for upper one
            _landslides_flag = os.path.basename(os.path.dirname(_img_path))

            _img = tiff()
            with open(_img_path, 'rb') as _rfp:
                _imgdata = _rfp.read()
                _img.parse(_imgdata)

                _before_size = _img.ifd_list.index(0).size()

                # add tag 'Occurrence Flag'
                _byteorder = _img.header.byteorder
                _tag = tag(_img.header, int(500).to_bytes(2, _byteorder))
                _datatype = datatype(_img.header, int(3).to_bytes(2, _byteorder))
                _count = int(1).to_bytes(4, _byteorder)
                _data = (1 if _landslides_flag == 'positive' and _mode == 'after' else 0 )
                _datapointer = int(_data).to_bytes(4, _byteorder)
                _ext_data = ifd_entry(_img.header).create(_tag, _datatype, _count, _datapointer)

                _img.addIFDEntry(0, _ext_data)

            with open(Path(_output_path + '/' + _img_path.name), 'wb') as _wfp:
                _wfp.write(_img.bytedata)

            self.__printBar(self.__total_size, _pi-1, _landslides_flag + ':' + str(_img_path))
            _pi = _pi + 1


    '''
    Attach Occurrence Flag(For test)
    '''
    def __attachOccurrenceFlag_Test(self, _mode, _gen_input_path, _output_path, _ans_filename):
        _dect_ansor = {}
        if _mode == 'after':
            with open(_ans_filename, 'r') as rfp:
                i = 1
                for line in rfp:
                    name_value = line.split()
                    _dect_ansor[name_value[0]] = name_value[1]
                    i = i + 1

        pi = 1
        for img_path in _gen_input_path:
            img = tiff()
            with open(img_path, 'rb') as rfp:
                imgdata = rfp.read()
                img.parse(imgdata)

                before_size = img.ifd_list.index(0).size()

                _byteorder = img.header.byteorder
                _tag = tag(img.header, int(500).to_bytes(2, _byteorder))
                _datatype = datatype(img.header, int(3).to_bytes(2, _byteorder))
                _count = int(1).to_bytes(4, _byteorder)
                _data = 0
                if _mode == 'after':
                    basename = os.path.basename(img_path)
                    if basename in _dect_ansor:
                        _data = _dect_ansor[basename]
                _datapointer = int(_data).to_bytes(4, _byteorder)
                _ext_data = ifd_entry(img.header).create(_tag, _datatype, _count, _datapointer)

                img.addIFDEntry(0, _ext_data)

            with open(Path(_output_path + '/' + img_path.name), 'wb') as wfp:
                wfp.write(img.bytedata)

            self.__printBar(self.__total_size, pi-1)
            pi = pi + 1


    '''
     Collect big region
    '''
    def collect(self, _path, _debug=False):
        print('[2/3] Collect group bit region.')
        _gen_file = Path(_path).glob('*.tif')
        _i = 0
        for _img_path in _gen_file:
            _split = _img_path.stem.split('_')
            if len(_split) != 4:
                print('[ERROR] file name "' + _img_path.name + '" format "{(train/test)}_{big_region_id}_{x}_{y}.tif"')
                break
            _groupnum = int(_split[1])
            _colnum = int(_split[2])
            _rownum = int(_split[3])

            _groupkey = _split[0] + '_' + str(_groupnum)

            if _groupkey not in self.__map_group:
                self.__map_group[_groupkey] = {}

            if _rownum not in self.__map_group[_groupkey]:
                self.__map_group[_groupkey][_rownum] = {}
            self.__map_group[_groupkey][_rownum][_colnum] = {}
            self.__map_group[_groupkey][_rownum][_colnum] = TiffInfo(_img_path)

            self.__printBar(self.__total_size, _i)
            _i = _i + 1

        if _debug:
            self.__dump()


    '''
    Create big region group Tiff file
    '''
    def create(self, _output_path, src_delete=False):
        print('[3/3] Create big region group Tiff file.')
        _total_count = len(self.__map_group)
        _header = header()
        _header.create('little', 8)     # IFD is next header

        _gi = 1
        for _groupkey in sorted(self.__map_group.keys()):
            _groupval = self.__map_group[_groupkey]
            _defaultifd = None
            _img_width = _img_height = 0
            _img_list = []
            for _rowkey in sorted(_groupval.keys()):
                _img_height = _img_height + self.__IMG_HEIGHT
                _img_width = 0
                for _colkey in sorted(_groupval[_rowkey].keys()):
                    _img_width = _img_width + self.__IMG_WIDTH
                    _defaultifd = _groupval[_rowkey][_colkey].tif.ifd_list
                    _imginfo = _groupval[_rowkey][_colkey]
                    _img_list.append(os.path.basename(_imginfo.path))
            _bdata = self.__connectData(_groupval)
            _ifd = ifd(_header)
            _ifd.add(self.__createIFDinfo(_header, _defaultifd, _img_width, _img_height, _img_list, _bdata))
            _ifd_supplement = str(_img_list).encode()

            _output_file = self.__outputTiff(_output_path, _groupkey, _header, _ifd, _ifd_supplement, _bdata)
            self.__printBar(self.__total_size, _gi, _output_file)
            _gi = _gi + 1


    def __createIFDinfo(self, _header, _default_ifd, _img_width, _img_height, _img_list, _data):
        _ifd_info = ifd_info(_header)
        # ImageWidth
        _tag_ImageWidth = tag(_header, 256)
        _datatype_ImageWidth = datatype(_header, 4)
        _ifd_info.addEntry(ifd_entry(_header).create(_tag_ImageWidth, _datatype_ImageWidth, 1, _img_width))
        # ImageLength
        _tag_ImageLength = tag(_header, 257)
        _datatype_ImageLength = datatype(_header, 4)
        _ifd_info.addEntry(ifd_entry(_header).create(_tag_ImageLength, _datatype_ImageLength, 1, _img_height))
        # BitsPerSample(default)
        _ifd_BitsPerSample = _default_ifd.searchTag(258)
        if _ifd_BitsPerSample == None:
            raise LookupError('tag<BitsPerSample> is not found.')
        _ifd_info.addEntry(ifd_entry(_header).create(_ifd_BitsPerSample.tag, _ifd_BitsPerSample.datatype, _ifd_BitsPerSample.count, _ifd_BitsPerSample.data_pointer))
        # Compression(default)
        _ifd_Compression = _default_ifd.searchTag(259)
        if _ifd_Compression == None:
            raise LookupError('tag<Compression> is not found.')
        _ifd_info.addEntry(ifd_entry(_header).create(_ifd_Compression.tag, _ifd_Compression.datatype, _ifd_Compression.count, _ifd_Compression.data_pointer))
        # PhotometricInterpretation(default)
        _ifd_photomtrc_inpre = _default_ifd.searchTag(262)
        if _ifd_photomtrc_inpre == None:
            raise LookupError('tag<PhotometricInterpretation> is not found.')
        _ifd_info.addEntry(ifd_entry(_header).create(_ifd_photomtrc_inpre.tag, _ifd_photomtrc_inpre.datatype, _ifd_photomtrc_inpre.count, _ifd_photomtrc_inpre.data_pointer))
        # RowsPerStrip
        _tag_RowsPerStrip = tag(_header, 278)
        _datatype_RowsPerStrip = datatype(_header, 4)
        _datapointer_RowsPerStrip = int(len(_data) / _img_width)
        _ifd_info.addEntry(ifd_entry(_header).create(_tag_RowsPerStrip, _datatype_RowsPerStrip, 1, _datapointer_RowsPerStrip))
        # StripByteCounts
        _tag_StripByteCounts = tag(_header, 279)
        _datatype_StripByteCounts = datatype(_header, 4)
        _ifd_info.addEntry(ifd_entry(_header).create(_tag_StripByteCounts, _datatype_StripByteCounts, 1, len(_data)))
        # OccurrenceFlag(custom)
        _ifd_OccurrenceFlag = _default_ifd.searchTag(500)
        if _ifd_OccurrenceFlag == None:
            print('tag<OccurrenceFlag(500)> is not found.')
        else:
            _ifd_info.addEntry(ifd_entry(_header).create(_ifd_OccurrenceFlag.tag, _ifd_OccurrenceFlag.datatype, _ifd_OccurrenceFlag.count, _ifd_OccurrenceFlag.data_pointer))
        # ImageName(option)
        _file_list = str(_img_list)
        _tag_FileList = tag(_header, 305)
        _datatype_FileList = datatype(_header, 2)
        _data_pointer_FileList = 8 + (2 + 12*(_ifd_info.size()+2) + 4)           # header(8) + ifd_entry_count(2) + ifd_entry(12)*ifd_entry_count + next_ifd_pointer(4) + ifd_data
        _ifd_info.addEntry(ifd_entry(_header).create(_tag_FileList, _datatype_FileList, len(_file_list.encode()), _data_pointer_FileList))
        # StripOffsets
        _tag_StripOffsets = tag(_header, 273)
        _datatype_StripOffsets = datatype(_header, 4)
        _datapointer_StripOffsets = _data_pointer_FileList + len(_file_list)
        _ifd_info.addEntry(ifd_entry(_header).create(_tag_StripOffsets, _datatype_StripOffsets, 1, _datapointer_StripOffsets))

        return _ifd_info


    '''
    Connect Tiff data
    '''
    def __connectData(self, _groupval):
        _data = bytes()
        for _rowkey in sorted(_groupval.keys()):
            _start_offset = 0
            _end_offset = self.__IMG_WIDTH * 2
            for _rownum in range(self.__IMG_HEIGHT):
                _row_data = bytes()
                for _colkey in sorted(_groupval[_rowkey].keys()):
                    _tif_data = _groupval[_rowkey][_colkey].tif.data
                    _data = butil.join(_data, _tif_data[_start_offset:_end_offset])
                _start_offset = _end_offset
                _end_offset = _end_offset + (self.__IMG_WIDTH * 2)
        return _data


    '''
     Output TIFF file
    '''
    def __outputTiff(self, _output_path, _groupkey, _header, _ifd, _ifd_supplement, _data):
        _output_file =   _output_path + '/' + str(_groupkey) + '.tiff'
        with open(_output_file, 'wb') as wfp:
            _bytedata = _header.bytedata
            while _ifd.hasNext():   # ifd is loop bat one section
                _ifd_info = _ifd.next()
                _bytedata = join(_bytedata, _ifd_info.bytedata)
            _bytedata = join(_bytedata, _ifd_supplement)
            _bytedata = join(_bytedata, _data)
            wfp.write(_bytedata)
        return _output_file



    def __dump(self):
        for _groupnum, _group in sorted(self.__map_group.items()):
            print('---------' + str(_groupnum) + '--------------')
            for _rownum, _row in sorted(self.__map_group[_groupnum].items()):
                sys.stdout.write(format(_rownum, '02d') + ': ')
                for _colnum, _col in sorted(self.__map_group[_groupnum][_rownum].items()):
                    sys.stdout.write(self.__map_group[_groupnum][_rownum][_colnum].path.name + ' ')
                print('')
            print('')


    def __printBar(self, _total, _now, _output_file=""):
        _prog = int((_now/_total) * 100)
        _bar = ['#' for i in range(int(_prog/2))]
        print(str(_prog) + '% : ' + ''.join(_bar))
        print(_output_file)
        if _prog != 100:
#            print("\u001B[2A", end="")
            print('\u001B[2A', end="")
        else:
            print('\u001B[3B', end="")


if __name__ == '__main__':
    _bigregion = BigRegion(40, 40)
#    _bigregion.attachOccurrenceFlag('before', '../resources/input/test/PALSAR/before', '../resources/input/sample_submit.tsv', '../resources/temp')
    _bigregion.collect('../resources/temp', _debug=False)
    _bigregion.create('../resources/output/1_pre/before', src_delete=True)



