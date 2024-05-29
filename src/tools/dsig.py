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
            self.intg[1:] = [self.intg[j] + self.intg[j-1] - self.quant for j in range(1, self.deg)]
            self.quant = 1 if self.intg[-1] > 0 else -1
            bitstream[i] = 1 if self.quant==1 else 0

        return np.packbits([int(b) for b in bitstream.astype(np.uint8)])
