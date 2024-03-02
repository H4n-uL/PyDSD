import numpy as np

class DeltaSigma:
    def __init__(self, deg=2):
        self.deg = deg
        self.intg = [0]*deg
        self.quant = 0
        self.ly = 0

    def modulator(self, x):
        assert self.deg > 0, 'ΔΣ modulator degree should be greater than 0.'
        bitstream = np.zeros_like(x)

        for i in range(len(x)):
            self.intg[0] += x[i] - self.quant
            for j in range(1, self.deg):
                self.intg[j] += self.intg[j-1] - self.quant
            self.quant = 1 if self.intg[-1] > 0 else -1
            bitstream[i] = 1 if self.quant==1 else 0

        return np.packbits([int(b) for b in bitstream.astype(np.uint8)])

    def demodulator(self, bitstream):
        bitstream = np.unpackbits(bitstream)
        y = np.zeros_like(bitstream, dtype=np.float64)

        for i in range(len(bitstream)):
            self.quant = 1 if bitstream[i] == 1 else -1
            for j in range(self.deg-1, 0, -1):
                self.intg[j] = self.intg[j-1]
            self.intg[0] = self.quant
            y[i] = self.intg[-1]

        return y