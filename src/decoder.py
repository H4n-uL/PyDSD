import argparse, struct
from scipy.signal import resample_poly
import numpy as np
from tools.dsig import DeltaSigma
import sounddevice as sd

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyDSD Decoder')
    parser.add_argument('input',                                                    help='Input file path')
    parser.add_argument('-o', '--output', '--out', '--output_file', required=False, help='Output file path')
    parser.add_argument('-m', '--mult', '--multipler',              required=False, help='DSD Sample rate multiplier')
    args = parser.parse_args()

    file_path = args.input
    
    with open(file_path, 'rb') as dsd:
        frm8 = dsd.read(32)
        proplen = struct.unpack('>Q', dsd.read(12)[4:])[0]
        prop = dsd.read(proplen)
        fs, chnl = prop.find(b'FS  ')+4, prop.find(b'CHNL')+4
        sample_rate = struct.unpack('>I', prop[fs+8:fs+12])[0]
        channels = struct.unpack('>H', prop[chnl+8:chnl+10])[0]

        BUFFER_SIZE = 262144
        
        dsd.read(12)
        stream = sd.OutputStream(samplerate=352800, channels=channels)
        stream.start()

        delta_sigma = [DeltaSigma() for _ in range(channels)]
        while True:
            block = dsd.read(BUFFER_SIZE*channels)
            if not block: break
            block = np.frombuffer(block, dtype=np.uint8).reshape(-1, channels)
            block = np.column_stack([resample_poly(delta_sigma[c].demodulator(block[:, c]),up=1,down=8) for c in range(channels)])

            play=True
            if play:
                stream.write(block.astype(np.float32))
            # else:
            #     pcm.write(block.tobytes())
