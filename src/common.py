import base64, os, platform, secrets

class variables:
    directory = os.path.dirname(os.path.realpath(__file__))
    tmpdir = os.path.join(directory, 'tempfiles')
    os.makedirs(tmpdir, exist_ok=True)
    temp_pcm = os.path.join(tmpdir, f'temp.{  base64.b64encode(secrets.token_bytes(64)).decode().replace("/", "_")}.pcm')
    temp_dsd = os.path.join(tmpdir, f'temp.{  base64.b64encode(secrets.token_bytes(64)).decode().replace("/", "_")}.bitstream')

    oper = platform.uname()
    arch = platform.machine().lower()

    if oper.system == 'Windows' and arch in ['amd64', 'x86_64']:
        ffmpeg =      os.path.join(directory, 'res', 'ffmpeg.Windows')
    elif oper.system == 'Darwin':
        ffmpeg =      os.path.join(directory, 'res', 'ffmpeg.macOS')
    else:
        if arch in ['amd64', 'x86_64']:
            ffmpeg =  os.path.join(directory, 'res', 'ffmpeg.AMD64')
        if arch == 'arm64':
            ffmpeg =  os.path.join(directory, 'res', 'ffmpeg.AArch64')
