import argparse, struct, subprocess
from common import variables
from scipy.signal import resample_poly
import numpy as np
from tools.dsig import DeltaSigma
import sounddevice as sd

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyDSD Decoder')
    parser.add_argument('input',                                                    help='Input file path')
    parser.add_argument('-o', '--output', '--out', '--output_file', required=False, help='Output file path')
    args = parser.parse_args()

    file_path = args.input
    
    with open(file_path, 'rb') as dsd:
        frm8 = dsd.read(32)
        proplen = struct.unpack('>Q', dsd.read(12)[4:])[0]
        prop = dsd.read(proplen)
        fs, chnl = prop.find(b'FS  ')+4, prop.find(b'CHNL')+4
        sample_rate = struct.unpack('>I', prop[fs+8:fs+12])[0]
        channels = struct.unpack('>H', prop[chnl+8:chnl+10])[0]

        if args.output is not None:
            command = [
                variables.ffmpeg, '-y',
                '-v', 'quiet',
                '-f', 'f64le',
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-i', 'pipe:0',
                '-ar', str(352800),
                # '-f', 'f64le',
                '-c:a', 'flac',
                '-sample_fmt', 's32',
                args.output+'.flac'
            ]
            
            pipe = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        BUFFER_SIZE = 2048
        
        dlen = struct.unpack('>Q', dsd.read(12)[4:])[0]
        stream = sd.OutputStream(samplerate=352800, channels=channels)
        stream.start()

        delta_sigma = [DeltaSigma() for _ in range(channels)]
        offset=0
        while True:
            if dlen < offset+BUFFER_SIZE*channels: block = dsd.read(dlen-offset)
            else: block = dsd.read(BUFFER_SIZE*channels)
            if not block: break
            offset += len(block)
            block = np.frombuffer(block, dtype=np.uint8).reshape(-1, channels)
            block = np.column_stack([(np.unpackbits(block[:, c]).astype(np.float64)-0.5)*2 for c in range(channels)])

            play=True
            if args.output is not None:
                pipe.stdin.write(block.newbyteorder('<').tobytes())
            else:
                stream.write(resample_poly(block,up=1,down=8).astype(np.float32))
            
            if dlen == offset: break
