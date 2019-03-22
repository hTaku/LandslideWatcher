def join(data1, data2):
    l = [data1[i] for i in range(len(data1))]
    l.extend([data2[i] for i in range(len(data2))])
    return bytes(l)

def replaceBytes(_bytedata, start_index, repbyte):
    _buffer = _bytedata[0:start_index]
    _buffer = join(_buffer, repbyte)
    return join(_buffer, _bytedata[start_index+len(repbyte):])

