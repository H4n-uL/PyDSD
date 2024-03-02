import base64, struct

class build:
    def dff_header(datalen: int, channels: int, sample_rate: int):
        CMPR = base64.b64decode('RFNEIA9ub3QgY29tcHJlc3NlZAA=')

        PROP = bytes(
            b'SND ' + \
            b'FS  ' + struct.pack('>Q', 4) + struct.pack('>I', sample_rate) +
            b'CHNL' + struct.pack('>Q', 2+len(b''.join(channels))) + struct.pack('>H', len(channels)) + b''.join(channels) +
            b'CMPR' + struct.pack('>Q', len(CMPR)) + CMPR
        )

        HEAD = bytearray(\
            b'FRM8' + \
            b'\x00'*8 + \
            b'DSD ' + \
            b'FVER' + struct.pack('>Q', 4) + b'\x01\x05\x00\x00' + \
            b'PROP' + struct.pack('>Q', len(PROP)) + PROP + \
            b'DSD ' + struct.pack('>Q', datalen)
        )

        HEAD[4:12] = struct.pack('>Q', datalen+len(HEAD))

        return HEAD
