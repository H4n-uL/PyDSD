import base64, os, platform, secrets, subprocess, sys

directory = os.path.dirname(os.path.realpath(__file__))
res = os.path.join(directory, 'res')

class variables:
    directory = os.path.dirname(os.path.realpath(__file__))
    tmpdir = os.path.join(directory, 'tempfiles')
    os.makedirs(tmpdir, exist_ok=True)
    temp_pcm = os.path.join(tmpdir, f'temp.{  base64.b64encode(secrets.token_bytes(64)).decode().replace("/", "_")}.pcm')
    temp_dsd = os.path.join(tmpdir, f'temp.{  base64.b64encode(secrets.token_bytes(64)).decode().replace("/", "_")}.bitstream')

    oper = platform.uname()
    arch = platform.machine().lower()

    resfiles = lambda x: [f for f in os.listdir(res) if x in f]
    try:    ffmpeg  = os.path.join(res, resfiles('ffmpeg')[0])
    except: ffmpeg  = 'ffmpeg'
    try:    ffprobe = os.path.join(res, resfiles('ffprobe')[0])
    except: ffprobe = 'ffprobe'

    try:
        subprocess.run([ffmpeg,  '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([ffprobe, '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print('Error: ffmpeg or ffprobe not found. Please install and try again,')
        print(f'or download and put them in {res}')
        sys.exit(1)