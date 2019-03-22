from utils.lang.byte_util import *

class header:
    bytedata = bytes()
    byteorder = str()
    version = bytes()
    ifd_addr = 0

    def __init__(self):
        pass

    def parse(self, data):
        self.bytedata = data[0:8];

        self.byteorder = 'big' if str(data[0:2].hex()) == '4d4d' else 'little'
        self.version = data[2:4]
        self.ifd_addr = int.from_bytes(data[4:8], self.byteorder)

    def create(self, _byteorder, _ifd_addr):
        self.byteorder = _byteorder
        self.version = int(42).to_bytes(2, _byteorder)
        self.ifd_addr = _ifd_addr
        _border = bytes.fromhex(('4949' if 'little' == _byteorder else '4D4D'))
        _bifdadd = int(_ifd_addr).to_bytes(4, _byteorder)
        self.bytedata = join(join(_border, self.version), _bifdadd)
        return self.bytedata

class tag:
    '''
     IFDタグ
    '''
    __tag_dict = {
        # 必須
        256: 'ImageWidth',
        257: 'ImageLength',
        258: 'BitsPerSample',
        259: 'Compression',
        262: 'PhotometricInterpretation',
        273: 'StripOffsets',
        278: 'RowsPerStrip',
        279: 'StripByteCounts',
        282: 'Xresolusion',
        283: 'Yresolusion',
        296: 'ResolutionUnit',
        320: 'ColorMap',
        # その他
        284: 'PlanarConfiguration'
    }

    bytedata = bytes()
    string = str()
    code = 0

    def __init__(self, header, data):
        _bdata = bytes()
        _idata = int(0)
        if type(data) == int:
            _bdata = int(data).to_bytes(2, header.byteorder)
            _idata = data
        elif type(data) == bytes:
            _bdata = data
            _idata = int.from_bytes(data, header.byteorder)
        self.bytedata = _bdata
        self.code = _idata
        _string = str(self.code)
        if self.code in self.__tag_dict:
            _string = self.__tag_dict[self.code]
        self.string = _string

class datatype:
    __datatype_dict = {
        1:  ['byte',      1],
        2:  ['ascii',     1],
        3:  ['short',     2],
        4:  ['long',      4],
        5:  ['rational',  8],
        6:  ['sbyte',     1],
        7:  ['undefined', 1],
        8:  ['sshort',    2],
        9:  ['slong',     4],
        10: ['srational', 8],
        11: ['float',     4],
        12: ['double',    8],
    }
    bytedata = bytes()
    string = str()
    code = 0
    size = 0

    def __init__(self, header, data):
        _bdata = bytes()
        _idata = int(0)
        if type(data) == int:
            _bdata = int(data).to_bytes(2, header.byteorder)
            _idata = data
        elif type(data) == bytes:
            _bdata = data
            _idata = int.from_bytes(data, header.byteorder)
        self.bytedata = _bdata
        self.code = _idata
        _string = str(self.code)
        if self.code in self.__datatype_dict:
            _string = self.__datatype_dict[self.code][0]
        self.string = _string
        self.size = self.__datatype_dict[self.code][1]

class ifd_data:
    bytedata = None

    def __init__(self, _bytedata):
        self.bytedata = _bytedata

class ifd_entry:
    bytedata = bytes()
    __header = None
    tag = None
    datatype = None
    count = 0
    data_pointer = 0

    def __init__(self, header):
        self.__header = header

    def create(self, tag, datatype, count, data_pointer):
        _bcount = bytes()
        _bdata_pointer = bytes()
        if type(count) == int:
            _bcount = int(count).to_bytes(4, self.__header.byteorder)
        elif type(count) == bytes:
            _bcount = count
        else:
            raise AttributeError('"count" is "integer" or "bytes". [' + str(type(count)) + ']')
        if type(data_pointer) == int:
            _bdata_pointer = int(data_pointer).to_bytes(4, self.__header.byteorder)
        elif type(data_pointer) == bytes:
            _bdata_pointer = data_pointer
        else:
            raise AttributeError('"data_pointer" is "integer" or "bytes". [' + str(type(data_pointer)) + ']')
        self.bytedata = join(join(join(tag.bytedata, datatype.bytedata), _bcount), _bdata_pointer)
        self.parse(self.bytedata)
        return self
    
    def replaceData(self, value):
        self.data_pointer = value

        countbyte = int(self.count).to_bytes(4, self.__header.byteorder)
        valuebyte = int(value).to_bytes(4, self.__header.byteorder)
        self.bytedata = join(self.tag.bytedata, join(self.datatype.bytedata, join(countbyte, valuebyte)))
        self.parse(self.bytedata)


    def parse(self, data):
        self.bytedata = data
        self.tag = tag(self.__header, data[0:2])
        self.datatype = datatype(self.__header, data[2:2+2])
        self.count = int.from_bytes(data[4:4+4], self.__header.byteorder)
        self.data_pointer = int.from_bytes(data[8:8+4], self.__header.byteorder)


class ifd_info:
    bytedata = bytes()
    __header = None
    count = 0
    __entrys = []
    next_pointer = 0
    __index = 0
    
    def __init__(self, header):
        self.__header = header

    def parse(self, data):
        self.count = int.from_bytes(data[0:2], self.__header.byteorder)
        addr = 2
        self.__entrys = []
        for i in range(self.count):
            __entry = ifd_entry(self.__header)
            __entry.parse(data[addr:addr+12])
            self.__entrys.append(__entry)
            addr = addr + 12
        self.next_pointer = int.from_bytes(data[addr:addr+4], self.__header.byteorder)
        self.bytedata = data[0:2+(12*self.count)+4]
        return self.count

    def hasEntryNext(self):
        return len(self.__entrys) > self.__index

    def nextEntry(self):
        result = self.__entrys[self.__index]
        self.__index = self.__index + 1
        return result

    def set_first(self):
        self.__index = 0

    def addEntry(self, entry):
        _entry_count = int.from_bytes(self.bytedata[0:2], self.__header.byteorder) + 1
        buffer = int(_entry_count).to_bytes(2, self.__header.byteorder)
        addr = 2
        for i in range(len(self.__entrys)):
            if self.__entrys[i].tag.code == 273:
                # modifide StripOffsets(273)
                self.__entrys[i].replaceData(self.__entrys[i].data_pointer + 12)  # shift 12byte
            buffer = join(buffer, self.__entrys[i].bytedata)
            addr = addr + 12
        buffer = join(buffer, entry.bytedata)
        if self.next_pointer != 0:
            self.next_pointer = self.next_pointer + 12  # shift 12byte [next_pointer]
        self.bytedata = join(buffer, int(self.next_pointer).to_bytes(4, self.__header.byteorder))
        self.parse(self.bytedata)
        return self.bytedata

    def searchTag(self, target):
        result = None
        for i in range(len(self.__entrys)):
            _entry = self.__entrys[i]
            if _entry.tag.code == target:
                result = _entry
                break
        return result

    def size(self):
        return len(self.__entrys)

class ifd:
    __header = None
    bytedata_list = []
    __ifd_info_list = []
    __index = 0
    __count = 0

    def __init__(self, header):
        self.__header = header
        ifd_entry(header)
        self.__ifd_info_list.clear()
        self.bytedata_list.clear()

    def parse(self, data):
        self.bytedata = data
        buffer = data
        addr = 0
        self.bytedata_list = []
        self.__ifd_info_list = []
        while True:
            self.__count = self.__count + 1
            ifd_data = ifd_info(self.__header)
            _count = ifd_data.parse(buffer)
            self.bytedata_list.append(data[addr:addr+2+(12*_count)+4])
            self.__ifd_info_list.append(ifd_data)
            if ifd_data.next_pointer == 0:
                break
            buffer = data[addr:]

    def hasNext(self):
        return len(self.__ifd_info_list) > self.__index

    def next(self):
        result = self.__ifd_info_list[self.__index]
        self.__index = self.__index + 1
        return result

    def set_first(self):
        self.__index = 0

    def index(self, index):
        self.__index = index
        return self.__ifd_info_list[index]

    def addEntry(self, index, entry):
        bytedata = self.__ifd_info_list[index].addEntry(entry)
        self.bytedata_list[index] = bytedata

    '''
    ' IFDを追加する
    ' @param _ifd_info    追加するIFD
    ' @param _set_pointer IFDを追加するバイト位置。
    '                     先頭のIDFに追加する場合は指定不要
    '''
    def add(self, _ifd_info, _set_pointer = 0):
        if _set_pointer != 0:
            if self.__count != 0:
                self.__ifd_info_list[self.__count].next_pointer = _set_pointer
                _bytedata = self.__ifd_info_list[self.__count].bytedata
                _bytedata = join(_bytedata[:4], int(_set_pointer).to_bytes(4, self.__header.byteorder))
                self.__ifd_info_list[self.__count].bytedata = _bytedata
                self.__bytedata_list[self.__count] = _bytedata
        else:
            if len(self.__ifd_info_list) != 0:
                self.__ifd_info_list.clear()
                self.bytedata_list.clear()
                self.__count = 0
        self.__ifd_info_list.append(_ifd_info)
        self.bytedata_list.append(_ifd_info.bytedata)
        self.__count = self.__count + 1

    def searchTag(self, target):
        entry = None
        for i in range(len(self.__ifd_info_list)):
            _ifd_info = self.__ifd_info_list[i]
            entry = _ifd_info.searchTag(target)
            if entry != None:
                break

        return entry

    def size(self):
        return len(self.__ifd_info_list)


class tiff:
    bytedata = bytes()
    header = None
    ifd_list = None
    ifd_data = {}
    byteorder = str()
    data = bytes()

    def __init__(self):
        pass

    def parse(self, _bytedata):
        self.bytedata = _bytedata
        self.header = header()
        self.header.parse(_bytedata)
        self.byteorder = self.header.byteorder
        self.ifd_list = ifd(self.header)
        self.ifd_list.parse(_bytedata[8:])
        # IFD data
        i = 1
        while self.ifd_list.hasNext():
            i = i + 1
            _ifd = self.ifd_list.next()
            while _ifd.hasEntryNext():
                _ifd_entry = _ifd.nextEntry()
                if _ifd_entry.count >= 2:
                    _ifd_data_addr_start = _ifd_entry.data_pointer
                    _ifd_data_addr_end = _ifd_data_addr_start + (_ifd_entry.count * _ifd_entry.datatype.size)
                    self.ifd_data[_ifd_entry] = ifd_data(_bytedata[_ifd_data_addr_start:_ifd_data_addr_end])
            _ifd.set_first()
        self.ifd_list.set_first()
        # data
        _strip_offset_entry = self.ifd_list.searchTag(273)  # StripOffsets
        _strip_byte_count = self.ifd_list.searchTag(279)    # StripByteCount
        if _strip_offset_entry != None and _strip_byte_count != None:
            _data_addr = _strip_offset_entry.data_pointer
            _data_count = _strip_byte_count.data_pointer
            self.data = _bytedata[_data_addr:_data_addr+_data_count]


    def addIFDEntry(self, index, entry):
        before_size = len(self.bytedata)
        self.ifd_list.addEntry(index, entry)
        _bytedata = replaceBytes(bytes(before_size+12), 0, self.header.bytedata)
        _ifd_pointer = self.header.ifd_addr
        while self.ifd_list.hasNext():
            _ifd = self.ifd_list.next()
            _bytedata = replaceBytes(_bytedata, _ifd_pointer, _ifd.bytedata)
            # IFD data
            while _ifd.hasEntryNext():
                _ifd_entry = _ifd.nextEntry()
                if _ifd_entry in self.ifd_data:
                    _ifd_data = self.ifd_data[_ifd_entry]
                    _bytedata = replaceBytes(_bytedata, _ifd_entry.data_pointer, _ifd_data.bytedata)
            _ifd.set_first()
            # data
            _data_pointer = _ifd.searchTag(273).data_pointer     # search StripOffset
            _bytedata = replaceBytes(_bytedata, _data_pointer, self.data)
            _ifd_pointer = _ifd.next_pointer
        self.ifd_list.set_first()
        self.parse(_bytedata)



