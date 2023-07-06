import numpy as np
import control.matlab as ctrl
import matplotlib.pyplot as plt

"""
  c1        x1   c2        x2
| +-|=|-+   ^    +-|=|-+   ^
|-+-///-+-| m1 |-+-///-+-| m2 |
|      k1   |         k2
            |    c3        x3
            |    +-|=|-+   ^
            +----+-///-+-| m3 |
                      k3

    +-| Ga |-+
|---*        +--- feedback
    +-| Gb |-+
  
Ga ... Tone Bar
Gb ... Tine  
"""
class TuningFork:
    """ToneBarとTineからなる構造体
    """
    def get_G(self, wn, zeta):
        return ctrl.tf((wn*wn), (1, 2.*zeta*wn, wn*wn))

    def get_zeta_for_Q(self, Q):
        return 1. / (2. * Q)

    # ニッケル合金の密度: 8.88 g/cm

    def __init__(self, f0: float, fbar: float, barQ: float, tineQ: float, note_num: int):
        """Tuning Forkの初期化

        Args:
            f0 (float): Tineの固有振動数
            fbar (float): Tone Barの固有振動数
            barQ (float): Tone BarのQ値
            tineQ (float): TineのQ値
        """
        # Tone Bar
        self._fa = fbar
        self._wa = 2. * np.pi * self._fa
        self._za = self.get_zeta_for_Q(barQ)
        self._Ga = self.get_G(self._wa, self._za)

        self._fb = f0
        self._wb = 2. * np.pi * self._fb
        self._zb = self.get_zeta_for_Q(tineQ)
        self._Gb = self.get_G(self._wb, self._zb)

        # TineはTonebarの影響を受けるからフィードバックで接続する
        self._Gf = ctrl.feedback(self._Ga, self._Gb)

        # 正規化した波形を保存する
        self._waveform, _ = self.impulse(np.arange(0, 10, 1./16000))
        maximum = np.max(np.abs(self._waveform))
        self._waveform *= maximum

    def get_waveform(self):
        return np.copy(self._waveform)

    def get_Gf(self):
        return self._Gf
    
    def impulse(self, t: np.ndarray):
        """任意の長さでインパルス応答を生成する

        Args:
            t (np.ndarray): 時刻を表す配列
        """
        y, T = ctrl.impulse(self._Gf, T=t)

        return y, T
    

class Magnet:
    def magnetic_slope(self, Z: np.ndarray):
        Y = [
            -2.37E-08,
            8.37E-07,
            -1.12E-05,
            6.78E-05,
            -1.61E-04
        ]
        # SIGN(Z1)*($Y$1*ABS(Z1)^5+$Y$2*Z1^4+$Y$3*ABS(Z1)^3+$Y$4*Z1^2+$Y$5*ABS(Z1))
        y = np.sign(Z) * (Y[0] * np.abs(Z)**5 + Y[1] * Z**4 + Y[2] * np.abs(Z)**3 + Y[3] * Z**2 + Y[4] * np.abs(Z))
        return Z, y

    def compute_waveform(self, fork: TuningFork, magnitude=1.0):
        wave = fork.get_waveform() * magnitude
        _, y = self.magnetic_slope(wave + self._offset)

        z = np.zeros_like(y)
        diff = 1. / self._fs
        for i in range(len(y) - 1):
            z[i] = (y[i+1] - y[i]) / diff

        return z

    def __init__(self, offset=0.0, fs=16000):
        self._fs = 16000
        self._offset = offset


class RhodesPiano:
    """複数のTuning Forkからなる楽器
    """
    def _get_pitch(self, concert_pitch, i):
        return concert_pitch * np.power(2., (i-69)/12)

    def __init__(self, concert_pitch=440., offset=4., fs=16000) -> None:
        N = 128
        self._f0s = [self._get_pitch(concert_pitch, i) for i in range(N)]
        self._forks = [TuningFork(self._f0s[i], self._f0s[i]/1.485, 1.09, 1.07, i) for i in range(N)]
        self._magnets = [Magnet(offset, fs) for i in range(N)]

    def electromotive_force(self, note_num: int, magnitude=1.0, fs=16000):
        y = self._magnets[note_num].compute_waveform(self._forks[note_num], magnitude)
        return y

    def impulse(self, midi_note_num: int, t: np.ndarray):
        return self._forks[midi_note_num].impulse(t)
    
    def bode(self, midi_note_num: int):
        return ctrl.bode(self._forks[midi_note_num].get_Gf(), Hz=True, dB=True)
    
    def bar_lengthes(self):
        return [x._la for i,x in enumerate(self._forks)]
    
    def tine_lengthes(self):
        return [x._lb for i,x in enumerate(self._forks)]


import wave, array
if __name__ == "__main__":
    
    fs = 16000
    rhodes = RhodesPiano(440., 1., fs)

    for i in range(128):
        print(i)
        y = rhodes.electromotive_force(i, 4.0)
        
        y = y / np.max(np.abs(y))
        y = y * 32767.
        y = np.asarray(y, dtype=np.int16)
    
        w = wave.Wave_write(f"electromotive/{i}.wav")
        w.setparams((
            1,                        # channel
            2,                        # byte width
            fs,                       # sampling rate
            len(y),                   # number of frames
            "NONE", "not compressed"  # no compression
        ))
        w.writeframes(y)
        w.close()

"""
Tone generator with vibratory bars

https://patentimages.storage.googleapis.com/5b/1a/f6/13bfe158f6a3e8/US3644656.pdf

捩じれたトーンバーに関する特許
f0 = 0.5596/L^2 = \sqrt{QK^2 / p}
L: 長さ
Q: ヤング率
K: 断面ねじりモーメント?
p: 密度

トーンバーの長さを求めるには、
1/f0 = L^2/0.5596
0.5596/f0 = L^2
L = sqrt(0.5596/f0)
"""