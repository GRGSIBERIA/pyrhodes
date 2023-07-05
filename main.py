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

    def __str__(self):
        return f"{self._la=}\n{self._lb=}"

    def get_Gf(self):
        return self._Gf
    
    def impulse(self, t: np.ndarray):
        """任意の長さでインパルス応答を生成する

        Args:
            t (np.ndarray): 時刻を表す配列
        """
        y, T = ctrl.impulse(self._Gf, T=t)

        return y, T

class RhodesPiano:
    """複数のTuning Forkからなる楽器
    """
    def _get_pitch(self, concert_pitch, i):
        return concert_pitch * np.power(2., (i-69)/12)

    def __init__(self, concert_pitch: 440.) -> None:
        N = 128
        self._f0s = [self._get_pitch(concert_pitch, i) for i in range(N)]
        self._forks = [TuningFork(self._f0s[i], self._f0s[i]/1.485, 1.09, 1.07, i) for i in range(N)]

        print(self._forks[36])

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
    
    rhodes = RhodesPiano(440.)

    for i in range(128):
        y, t = rhodes.impulse(i, np.arange(0, 10, 1./16000), )
        
        y = y / np.max(np.abs(y))
        y = y * 32767.
        y = np.asarray(y, dtype=np.int16)

        w = wave.Wave_write(f"wavs/{i}.wav")
        w.setparams((
            1,                        # channel
            2,                        # byte width
            16000,                    # sampling rate
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