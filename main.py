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
    def get_G(self, wn, zeta):
        return ctrl.tf((wn*wn), (1, 2.*zeta*wn, wn*wn))

    def get_critical_damping(self, m, w0):
        return 2. * m * w0

    def get_zeta(self, c, cc):
        return c / cc

    # meters
    def get_bar_length(self, f0):
        return np.sqrt(0.5596/f0)
    
    def get_tine_length(self, f0, m, E, I):
        xi = 1./(2. * np.pi * f0)
        return np.power((3. * E * I * xi) / m, 1./3.)

    def get_zeta_for_Q(self, Q):
        return 1. / (2. * Q)

    # ニッケル合金の密度: 8.88 g/cm

    def __init__(self, f0: float, fbar: float, tine_type: str, barQ: float, tineQ: float):
        """Tuning Forkの初期化

        Args:
            f0 (float): Tineの固有振動数
            fbar (float): Tone Barの固有振動数
            tine_type (str): Tineの種類, "long", "medium", "short"から選べる
            barQ (float): Tone BarのQ値
            tineQ (float): TineのQ値
        """
        # Tone Bar
        self._fa = fbar
        self._la = self.get_bar_length(fbar)
        self._wa = 2. * np.pi * self._fa
        self._ma = self._la * 8.88e-3 * 0.00254 * 0.0254
        self._za = self.get_zeta_for_Q(barQ)
        self._Ga = self.get_G(self._wa, self._za)

        # Tine
        if tine_type == "long":
            self._lb = 0.15
        elif tine_type == "medium":
            self._lb = 0.1
        elif tine_type == "short":
            self._lb = 0.05
        else:
            self._lb = self.get_bar_length(f0)

        self._fb = f0
        self._wb = 2. * np.pi * self._fb
        self._mb = 0.001524**2. * np.pi * self._lb * 7.84e-3
        yungs = 205e6
        moments = 2e-16    # 円の断面二次モーメント、メートルに変換
        self._lb = self.get_tine_length(f0, self._mb, yungs, moments)
        self._zb = self.get_zeta_for_Q(tineQ)
        self._Gb = self.get_G(self._wb, self._zb)

        # TineはTonebarの影響を受けるからフィードバックで接続する
        self._Gf = ctrl.feedback(self._Ga, self._Gb)

    
    def impulse(self, t: np.ndarray):
        """任意の長さでインパルス応答を生成する

        Args:
            t (np.ndarray): 時刻を表す配列
        """
        y, T = ctrl.impulse(self._Gf, T=t)

        return y, T

class RhodesPiano:
    def _get_pitch(self, concert_pitch, i):
        return concert_pitch * np.power(2., (i-69)/12)

    def __init__(self, concert_pitch: 440.) -> None:
        self._f0s = [self._get_pitch(concert_pitch, i) for i in range(88)]
        self._forks = [TuningFork(self._f0s[i], self._f0s[i]/2., "medium", 1.40, 1.47) for i in range(88)]

    def impulse(self, midi_note_num: int, t: np.ndarray):
        return self._forks[midi_note_num].impulse(t)

if __name__ == "__main__":
    
    rhodes = RhodesPiano(440.)
    y, t = rhodes.impulse(12, np.arange(0, 4, 0.01))
    
    plt.figure()
    plt.plot(t, y)
    plt.show()

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