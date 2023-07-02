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

def getDampingRatio(c, cc):
    return c / cc

if __name__ == "__main__":
    fa = 55.
    za = 0.2
    wa = 2. * np.pi * fa
    Ga = getG(wa, za)

    fb = 220.
    zb = 0.9
    wb = 2. * np.pi * fb
    Gb = getG(wb, zb)

    Gf = ctrl.feedback(Ga, Gb)

    print(Gf)

    t = np.arange(0, 2, 0.01)
    y, t = ctrl.impulse(Gf, T=t)

    plt.figure()
    plt.plot(t, y)
    plt.show()