with open('input.dsd', 'rb') as f_in, open('dsd.pcm', 'wb') as f_out:
    f_in.seek(130)
    while True:
        by = [f_in.read(1), f_in.read(1)]
        if not by[0] or not by[1]:
            break
        bits = [bin(int.from_bytes(byte, "big"))[2:].zfill(8) for byte in by]
        interleaved = ''.join(b for pair in zip(bits[0], bits[1]) for b in pair)
        interleaved = interleaved.replace('1', '\xff').replace('0', '\x00')
        f_out.write(bytes(interleaved, "latin1"))

# ffmpeg -y -loglevel error -f u8 -ar 2822400 -ac 2 -i dsd.pcm -c:a pcm_s16le -sample_fmt s16 16b.wav
