from utils.lang.byte_util import *
from utils.images.tiff import *

def printDebug(img):
    _byteorder = str(img.header.byteorder)
    print('[header]byteorder   : ' + _byteorder)
    print('[header]version     : 0x' + str(img.header.version.hex()))
    print('[header]ifd_pointer : ' + str(img.header.ifd_addr))
    _ifd_index = 0
    while img.ifd_list.hasNext():
        _ifd_info = img.ifd_list.next()
        print('    [ifd]entry count : ' + str(_ifd_info.count))
#        _ifd_info.set_first()
        _entry_index = 1 
        while _ifd_info.hasEntryNext():
            _ifd_entry = _ifd_info.nextEntry()
            prefix =  '        ifd[' + str(_ifd_index) + '].data[' + str(_entry_index) + ']'
            print(prefix + 'tag     : ' + _ifd_entry.tag.string + '(' + str(_ifd_entry.tag.code) + ')')
            print(prefix + 'datatype: ' + _ifd_entry.datatype.string)
            print(prefix + 'count   : ' + str(_ifd_entry.count))
            print(prefix + 'pointer : ' + hex(_ifd_entry.data_pointer))
            print('    ---------------------------------')
            _entry_index = _entry_index + 1
        print('    ifd[' + str(_ifd_index) + '].next pointer: ' + str(_ifd_info.next_pointer))
        _ifd_index = _ifd_index + 1

    img.ifd_list.set_first()


if __name__ == '__main__':
    img = tiff()
#    with open('../resources/input/test/PALSAR/before/test_0000_0_0.tif', 'rb') as rfp:
#    with open('../resources/output/test/PALSAR/before/1_pre/test_0.tiff', 'rb') as rfp:
    with open('../resources/output/test/PALSAR/after/1_pre/test_0.tiff', 'rb') as rfp:
        data = rfp.read()
        img.parse(data)

        _byteorder = str(img.header.byteorder)

        printDebug(img)

        print('--------------------------------')

#        _tag = tag(img.header, int(500).to_bytes(2, _byteorder))
#        _datatype = datatype(img.header, int(3).to_bytes(2, _byteorder))
#        _count = int(1).to_bytes(4, _byteorder)
#        _datapointer = int(1).to_bytes(4, _byteorder)
#        ext_data = ifd_entry(img.header).create(_tag, _datatype, bytearray(_count), bytearray(_datapointer))

#        img.addIFDEntry(0, ext_data)

#        printDebug(img)

#    with open('../resources/output/1_pre/test_0000_0_3.tif', 'wb') as wfp:
#        wfp.write(img.bytedata)


