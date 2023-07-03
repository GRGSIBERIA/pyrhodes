# 計算方法

## Tineの長さ

片持ち梁は

$$
f = \frac{1}{T} = \frac{1}{2\pi \sqrt{m/k}}
$$
で表せられる。ただし、
$$
k = \frac{3EI}{L^3}
$$

$m$は質量、$k$はバネ定数、$E$はヤング率、$I$は断面二次モーメント、$L$は長さである。Tineの長さを求めたいのであるから、$L$の式に直す必要がある。

まず、$f$の式だけに着目して式変形を行う。$f$から$k$の式に変形すると、

$$
f = \frac{1}{2\pi \sqrt{m/k}}
$$
$$
\frac{1}{f} = 2\pi \sqrt{m/k}
$$
$$
\frac{1}{2\pi f} = \sqrt{m/k}
$$
$$
\left(\frac{1}{2\pi f}\right)^2 = m/k
$$

ここで、式が複雑になるため$\xi$を導入する

$$
\xi = \left(\frac{1}{2\pi f}\right)^2 = m/k
$$
$$
\frac{1}{\xi} = k/m
$$
$$
\frac{m}{\xi} = k
$$

$k$の式で表せられるようになったので、$k$の式から$L$に変形する。

$$
\frac{m}{\xi} = \frac{3EI}{L^3}
$$
$$
\frac{\xi}{m} = \frac{L^3}{3EI}
$$
$$
\frac{3EI\xi}{m} = L^3
$$
$$
\left(\frac{3EI\xi}{m}\right)^{\frac{1}{3}} = \sqrt[3]{\frac{3EI\xi}{m}} = L
$$

よって、$f$, $m$, $E$, $I$がわかれば、$L$を示すことができる。

# 関連する特許

## Tone generator with vibratory bars

https://patentimages.storage.googleapis.com/5b/1a/f6/13bfe158f6a3e8/US3644656.pdf

トーンバーの構造に関する特許。トーンバーの適切な長さについて主張している。

## Tuning fork mounting assembly in electromechanical pianos

https://patentimages.storage.googleapis.com/e1/df/8b/aeb22561b97f68/US4373418.pdf

チューニングフォークの構造に関する特許。チューニングフォークを本体にマウントする方法に関する主張。