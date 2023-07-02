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

    # ニッケル合金の密度: 8.88 g/cm

    def __init__(self, f0: float, fbar: float):
        """Tuning Forkの初期化

        Args:
            f0 (float): Tineの固有振動数
            fbar (float): Tone Barの固有振動数
        """
        # Tone Bar
        self._fa = fbar
        self._la = self.get_bar_length(fbar)
        self._wa = 2. * np.pi * self._fa
        self._ma = self._la * 8.88e-6 * 0.00254 * 0.0254
        self._cca = self.get_critical_damping(self._ma, self._wa)
        self._za = self.get_zeta(14., self._cca)
        self._Ga = self.get_G(self._wa, self._za)

        # Tine
        self._fb = f0
        self._wb = 2. * np.pi * self._fb
        self._lb = self.get_bar_length(f0)
        self._mb = self._lb * 8.86e-6
        self._ccb = self.get_critical_damping(self._mb, self._wb)
        self._zb = self.get_zeta(14., self._ccb)
        self._Gb = self.get_G(self._wb, self._zb)

        self._Gf = ctrl.feedback(self._Ga, self._Gb)

        print(self._ccb)
    
    def impulse(self, t: np.ndarray):
        """任意の長さでインパルス応答を生成する

        Args:
            t (np.ndarray): 時刻を表す配列
        """
        y, T = ctrl.impulse(self._Gf, T=t)

        return y, T

if __name__ == "__main__":
    
    fork = TuningFork(440, 440)

    y, t = fork.impulse(np.arange(0, 4, 0.01))
    
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