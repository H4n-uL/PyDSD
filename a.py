import struct

with open('input.dsd', 'rb') as f_in, open('dsd.pcm', 'wb') as f_out:
    frm8 = f_in.read(32)
    proplen = struct.unpack('>Q', f_in.read(12)[4:])[0]
    prop = f_in.read(proplen)
    fs, chnl = prop.find(b'FS  ')+4, prop.find(b'CHNL')+4
    sample_rate = struct.unpack('>I', prop[fs+8:fs+12])[0]
    channels = struct.unpack('>H', prop[chnl+8:chnl+10])[0]
    dlen = struct.unpack('>Q', f_in.read(12)[4:])[0]
    for _ in range(0, dlen, channels):
        by = [f_in.read(1) for _ in range(channels)]
        if not by[0] or not by[1]:
            break
        bits = [bin(int.from_bytes(byte, "big"))[2:].zfill(8) for byte in by]
        interleaved = ''.join(b for pair in zip(bits[0], bits[1]) for b in pair)
        interleaved = interleaved.replace('1', '\xff').replace('0', '\x00')
        f_out.write(bytes(interleaved, "latin1"))

# ffmpeg -y -loglevel error -f u8 -ar 2822400 -ac 2 -i dsd.pcm -c:a pcm_s16le -sample_fmt s16 16b.wav
