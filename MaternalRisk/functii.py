import numpy as np
import scipy.stats as sts
from pandas import DataFrame
import collections
import scipy.linalg as lin

def putere_discriminare(ssb, ssw, n, q):
    r = (n - q) / (q - 1)
    f = r * np.diag(ssb) / np.diag(ssw)
    p_value = 1 - sts.f.cdf(f, q - 1, n - q)
    return f, p_value

# Calcul centrii, frecvente grupe, etichete grupe si matrice de imprastiere
# x - tabel date
# y - variabila de grupare
def imprastiere(x, y):
    n, m = np.shape(x)
    medii = np.mean(x, axis=0)
    counter = collections.Counter(y)
    g = np.array([i for i in counter.keys()])  # preluare etichete
    ng = np.array([i for i in counter.values()])  # preluare frecvente
    q = len(g)
    xg = np.ndarray(shape=(q, m))
    for k, i in zip(g, range(len(g))):
        xg[i, :] = np.mean(x[y == k, :], axis=0)
    xg_med = xg - medii
    sst = n * np.cov(x, rowvar=False, bias=True)
    ssb = np.transpose(xg_med) @ np.diag(ng) @ xg_med
    ssw = sst - ssb
    return g, ng, xg, sst, ssb, ssw


def imprastiere_(x, xg, ng):
    n, m = np.shape(x)
    medii = np.mean(x, axis=0)
    xg_med = xg - medii
    sst = n * np.cov(x, rowvar=False, bias=True)
    ssb = np.transpose(xg_med) @ np.diag(ng) @ xg_med
    ssw = sst - ssb
    return sst, ssb, ssw

def lda(sst, ssb, n, q):
    m = len(sst)
    cov_inv = np.linalg.inv(sst)
    h = cov_inv @ ssb
    if np.allclose(h, np.transpose(h)):
        valp, vecp = np.linalg.eig(h)
    else:
        c = lin.sqrtm(ssb)
        h = np.transpose(c) @ cov_inv @ c
        valp, vecp_ = np.linalg.eig(h)
        vecp = cov_inv @ c @ vecp_
    k_inv = np.flipud(np.argsort(valp))
    r = min(m, q - 1)
    alpha = np.real(valp[k_inv[:r]])
    u = np.real(vecp[:, k_inv[:r]])
    regularizare(u)
    l = alpha * (n - q) / ((1 - alpha) * (q - 1))
    return alpha, l, u

def regularizare(t, y=None):
    if type(t) is DataFrame:
        for c in t.columns:
            minim = t[c].min()
            maxim = t[c].max()
            if abs(minim) > abs(maxim):
                t[c] = -t[c]
                if y is not None:
                    k = t.columns.get_loc(c)  # determina indexul coloanei
                    y[:, k] = -y[:, k]
    else:
        for i in range(np.shape(t)[1]):
            minim = np.min(t[:, i])
            maxim = np.max(t[:, i])
            if np.abs(minim) > np.abs(maxim):
                t[:, i] = -t[:, i]

# Calcul functii de clasificare pe variabile discriminate
def functii_clasificare_z(z, zg, ng):
    n = np.shape(z)[0]
    q = np.shape(zg)[0]
    cov_inv = np.diag(1.0 / np.var(z, axis=0))
    f = zg @ cov_inv
    f0 = np.empty(shape=(q,))
    for i in range(q):
        f0[i] = -0.5 * f[i, :] @ zg[i, :]
    f0_b = f0 + np.log(ng / n)  # Termenii liberi pentru bayes
    return f, f0, f0_b

# Predictie pe baza functiilor de clasificare
def predict(x, f, f0, g):
    n, m = np.shape(x)
    clasif = np.empty(shape=(n,), dtype=np.int64)
    for i in range(n):
        rez = f @ x[i, :] + f0
        clasif[i] = np.argmax(rez)
    return g[clasif]

def tabelare_matrice(x, nume_linii=None, nume_coloane=None, out=None):
    t = DataFrame(x, nume_linii, nume_coloane)
    if out is not None:
        t.to_csv(out)
    return t


