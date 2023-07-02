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

def getG(wn, zeta):
    return ctrl.tf((wn*wn), (1, 2.*zeta*wn, wn*wn))

def getCriticalDamping(m, w0):
    return 2. * m * w0

def getZeta(c, cc):
    return c / cc

# meters
def getBarLength(f0):
    return np.sqrt(0.5596/f0)

if __name__ == "__main__":
    fa = 55.
    ma = 0.1
    wa = 2. * np.pi * fa
    cca = getCriticalDamping(ma, wa)
    za = getZeta(14., cca)
    Ga = getG(wa, za)
    print(getBarLength(44))

    fb = 220.
    mb = 0.01
    wb = 2. * np.pi * fb
    ccb = getCriticalDamping(mb, wb)
    zb = getZeta(27., ccb)
    Gb = getG(wb, zb)

    Gf = ctrl.feedback(Ga, Gb)

    print(Gf)

    t = np.arange(0, 4, 0.01)
    y, t = ctrl.impulse(Gf, T=t)

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