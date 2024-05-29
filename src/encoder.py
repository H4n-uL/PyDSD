import argparse, os, json, subprocess, shutil
from common import variables
import numpy as np
from tools.dsig import DeltaSigma
from tools.header import build

class dsd:
    channels_dict = {
        1: [b'SLFT'],
        2: [b'SLFT', b'SRGT'],
        3: [b'MLFT', b'MRGT', b'C   '],
        4: [b'MLFT', b'MRGT', b'LS  ', b'RS  '],
        5: [b'MLFT', b'MRGT', b'C   ', b'LS  ', b'RS  '],
        6: [b'MLFT', b'MRGT', b'C   ', b'LFE ', b'LS  ', b'RS  ']
    }

    def get_info(file_path):
        command = ['ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        info = json.loads(result.stdout)

        for stream in info['streams']:
            if stream['codec_type'] == 'audio':
                return int(stream['channels']), int(stream['sample_rate']), stream['codec_name']
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyDSD Encoder')
    parser.add_argument('input',                                                    help='Input file path')
    parser.add_argument('-o', '--output', '--out', '--output_file', required=False, help='Output file path')
    parser.add_argument('-m', '--mult', '--multipler',              required=False, help='DSD Sample rate multiplier')
    parser.add_argument('-p', '--pres', '--preserve',               action='store_true', help='Preserve bitstream')
    args = parser.parse_args()

    file_path = args.input

    if args.output is None: out = os.path.basename(file_path).rsplit('.', 1)[0]
    else: out = args.output
    if not (out.lower().endswith('.dsd') or out.lower().endswith('.dff')):
        out += '.dsd'

    if args.mult is not None and args.mult in '64 128 256 512 1024'.split():
        dsd_srate = 44100 * int(args.mult)
    else: dsd_srate = 2822400

    channels = dsd.get_info(file_path)[0]
    chb = dsd.channels_dict[channels]

    try:
        BUFFER_SIZE = 262144 * 4 * channels

        delta_sigma = [DeltaSigma() for _ in range(channels)]
        command = [
            variables.ffmpeg,
            '-v', 'quiet',
            '-i', file_path,
            '-f', 's32le',
            '-ar', str(dsd_srate),
            '-acodec', 'pcm_s32le',
            '-vn',
            'pipe:1'
        ]

        pipe = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        with open(variables.temp_dsd, 'wb') as bstr:
            while True:
                data = pipe.stdout.read(BUFFER_SIZE)
                if not data or data == b'': break
                # print(data)
                data_numpy = np.frombuffer(data, dtype=np.int32).astype(np.float64) / 2**32
                freq = [data_numpy[i::channels] for i in range(channels)]
                block = np.column_stack([delta_sigma[c].modulator(freq[c]) for c in range(len(freq))]).ravel(order='C').tobytes()

                bstr.write(block)
                dlen = os.path.getsize(variables.temp_dsd)
                h = build.dff_header(dlen, chb, dsd_srate)
            with open(out, 'wb') as f, open(variables.temp_dsd, 'rb') as temp:
                f.write(h + temp.read())
    except KeyboardInterrupt: pass
    finally:
        dlen = os.path.getsize(variables.temp_dsd)
        h = build.dff_header(dlen, chb, dsd_srate)
        with open(out, 'wb') as f, open(variables.temp_dsd, 'rb') as temp:
            f.write(h + temp.read())
        if args.pres: os.remove(variables.temp_dsd)
        else: shutil.move(variables.temp_dsd, f'{out}.bitstream')
