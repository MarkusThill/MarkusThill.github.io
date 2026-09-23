# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# $\renewcommand{\vec}[1]{\boldsymbol{\mathbf{#1}}}$
# $\def\matr#1{\boldsymbol{\mathbf{#1}}}$
# $\def\tp{\mathsf T}$
# $\newcommand{\E}{\mbox{I\negthinspace E}}$
#
# # Mahalanobis Distance: A Collection of Notes and Code Snippets
# - The Mahalanobis distance between two points $\vec x \in \mathbb{R}^n$ and $\vec y  \in \mathbb{R}^n$ is defined as
#
# \begin{align}
# d(\vec x,\vec y) = \sqrt{(\vec x -\vec y )^\tp \matr \Sigma^{-1} (\vec x - \vec y)},
# \end{align}
#
# where $\matr \Sigma$ is a covariance matrix, specifying the (co-)variances between individual features (dimensions) of a given dataset or distribution.
# - A common application of the Mahalanobis distance is to identify outliers in some given data. For this purpose, the Mahalanobis distance to the center (approximated by the sample mean) of the distribution is measured. The squared Mahalanobis distance of a vector $\matr x \in \mathbb{R}^n$ and the centroid $\vec \mu \in \mathbb{R}^n$ of the dataset is defined as:
#
# \begin{align}
# D = d(\matr X,\vec \mu)^2 = (\matr x -\vec \mu )^\tp \matr \Sigma^{-1} (\matr x - \vec \mu ), \label{eq:sqMahalanobis}
# \end{align}
#
# - For example, a possibly well-suited application in practice for the Mahalanobis distance could be detecting (multivariate) outlying reconstruction errors.
# - The Mahalanobis distance does not impose any conditions on the distribution of the data. It is not required that the data is Gaussian in order to compute the Mahalanobis distance (although we have some nice properties if it is the case)
# - There might be numerical issues, if the individual features (dimensions) are highly correlated (we need the inverse of the covariance matrix)
# - For very high-dimensional data (>10k dimensions), it becomes computationally expensive to compute the Mahalanobis distance. It makes sense to cache the inverse of the covariance matrix in this case
# - It is possible to compute the Mahalanobis distance between arbitrary points. In practice (see implementations below), commonly, the distance to the centroid is measured
# - Note that most approaches below actually compute the squared Mahalanobis Distance $D=d^2$
#
# ## Some more Side Notes
# - Calculating quantiles for multivariate normal distributions is not that trivial as in the one-dimensional case, since we cannot simply compute the integral under the distribution
# - The quantiles in the bivariate case can be seen as ellipses, in higher dimensions as ellipsoids
# - The Mahalanobis distance is an interesting measure to describe all points on the surface of an ellipsoid
# - In a naive solution one can use a Monte Carlo approach to sample the multivariate normal distribution and compute the quantile based on the Mahalanobis distances of the elements of the sample
# - However, this Monte Carlo approach is rather computationally inefficient, especially if quantiles have to be computed very often
# - One can show that the squared Mahalanobis distance of a Gaussian distribution is actually Chi-Square distributed (see below)
#
# ## Further Reading
# - https://en.wikipedia.org/wiki/Mahalanobis_distance
# - https://www.machinelearningplus.com/statistics/mahalanobis-distance/
# - https://www.statisticshowto.com/mahalanobis-distance/
# - https://stats.stackexchange.com/questions/62092/bottom-to-top-explanation-of-the-mahalanobis-distance

# %%

# %%
import os

os.environ["JAX_ENABLE_X64"] = "True"

import matplotlib as plt
import numpy as np
import jax.numpy as jnp
import tensorflow.keras.backend as K
import tensorflow as tf
import scipy


# %% [markdown]
# ## Offline Computation Approaches

# %%
def xnp_is_singular(X, eps=1e-7, xnp=jnp):
    sign, logdet = xnp.linalg.slogdet(X)  # Logartihm of determinant is more stable
    return logdet < xnp.log(eps)


def tf_is_singular(X, eps=1e-7):
    # only hermitian (symmetric) positive definite matrices are supported
    sign, logdet = tf.linalg.slogdet(X)
    return logdet.numpy() < np.log(eps)


def mahalanobis_distance_scipy(X, cov=None, mu=None, inv_cov=None, check_singular=True):
    if mu is None:
        mu = scipy.stats.tmean(X, axis=0)
    if cov is None:
        cov = np.cov(X, rowvar=False)  # scipy has no cov() function
    if inv_cov is None:
        if check_singular and xnp_is_singular(cov, xnp=np):
            raise NotImplementedError("Cannot determine the inverse of a singular matrix!")
        inv_cov = scipy.linalg.inv(cov)

    maha = []
    for x in X:
        maha.append(scipy.spatial.distance.mahalanobis(x, mu, inv_cov))
    return np.asarray(maha)


def mahalanobis_distance_slow(x=None, data=None, cov=None):
    """
    Not my implementation
    Taken from: https://www.machinelearningplus.com/statistics/mahalanobis-distance/
    Compute the Mahalanobis Distance between each row of x and the data
    x    : vector or matrix of data with, say, p columns.
    data : ndarray of the distribution from which Mahalanobis distance of each observation of x is to be computed.
    cov  : covariance matrix (p x p) of the distribution. If None, will be computed from data.
    """
    x_minus_mu = x - np.mean(data, axis=0)  # MT: corrected this line: added 'axis=0'
    if not cov:
        cov = np.cov(data.T)
    inv_covmat = scipy.linalg.inv(cov)
    left_term = np.dot(x_minus_mu, inv_covmat)
    mahal = np.dot(left_term, x_minus_mu.T)
    return mahal.diagonal()


def xnp_mahalanobis_distance(X, cov=None, mu=None, inv_cov=None, xnp=jnp, check_singular=True):
    """
    Computes the squared Mahalanobis distance of each data point (row)
    to the center of the distribution, described by cov and mu.
    (or any other point mu).
    If the parameters cov and mu are left empty, then this function
    will compute them based on the data X.
    """
    if mu is None:
        mu = xnp.mean(X, axis=0)
    if cov is None:
        cov = xnp.cov(X, rowvar=False)
    if inv_cov is None:
        if check_singular and xnp_is_singular(cov, xnp=xnp):
            raise NotImplementedError("Cannot determine the inverse of a singular matrix!")
        inv_cov = xnp.linalg.inv(cov)

    X_diff_mu = X - mu
    return xnp.apply_along_axis(lambda x: xnp.matmul(xnp.matmul(x, inv_cov), x.T), 1, X_diff_mu)


def xnp_mahalanobis_distance2(A, xnp=jnp, check_singular=True):
    mu = xnp.mean(A, axis=0, keepdims=False)
    M = A - mu
    cov = 1.0 / (A.shape[0] - 1) * xnp.dot(M.T, M)
    if check_singular and xnp_is_singular(cov, xnp=xnp):
        raise NotImplementedError("Cannot determine the inverse of a singular matrix!")

    X_mu_SInv = xnp.dot(M, xnp.linalg.inv(cov))
    return xnp.sum(X_mu_SInv * M, axis=1)


def tf_mat_inv(X):
    return tf.keras.layers.Lambda(lambda x: tf.linalg.inv(x))(X)


def tf_mahalanobis_distance(X, check_singular=True):
    A = K.variable(value=X)
    mu = K.mean(A, axis=0, keepdims=False)
    M = A - mu
    cov = 1.0 / (X.shape[0] - 1) * K.dot(K.transpose(M), M)

    if check_singular and tf_is_singular(cov):
        raise NotImplementedError("Cannot determine the inverse of a singular matrix:\n")

    A_mu_SInv = K.dot(M, tf_mat_inv(cov))
    A_mu_SInv_A_mu = tf.reduce_sum(A_mu_SInv * M, axis=1)

    return K.eval(A_mu_SInv_A_mu)



# %% [markdown]
# ## Example 1: Mahalanobis Distances for 2-dimensional Dataset

# %%
cov = np.array([[15, -3], [-3, 3.5]])
X = np.random.multivariate_normal([0, 0], cov, size=5000).astype("float32")  # float32 for a fair comparison of timings

# %%
### Ensure that all the results are the same
assert np.abs(mahalanobis_distance_slow(x=X, data=X) - xnp_mahalanobis_distance(X, xnp=jnp)).mean() < 1e-6
assert np.abs(xnp_mahalanobis_distance(X, xnp=np) - xnp_mahalanobis_distance(X, xnp=jnp)).mean() < 1e-6
assert np.abs(xnp_mahalanobis_distance(X, xnp=np) - tf_mahalanobis_distance(X)).mean() < 1e-6
assert np.abs(xnp_mahalanobis_distance(X, xnp=jnp) - tf_mahalanobis_distance(X)).mean() < 1e-6
assert np.abs(xnp_mahalanobis_distance2(X, xnp=np) - tf_mahalanobis_distance(X)).mean() < 1e-6
assert np.abs(xnp_mahalanobis_distance2(X, xnp=jnp) - tf_mahalanobis_distance(X)).mean() < 1e-6
assert (np.abs(np.sqrt(xnp_mahalanobis_distance2(X, xnp=jnp)) - mahalanobis_distance_scipy(X)).mean() < 1e-2)  # Quite big differences... Where do they come from?


# %%
### Timings for the individual variants (2-dim. distribution)
# Note that for smaller dimensions the GPU variants do not have any advantage

check_singular_cov = True # For small covariance matrices this can be set to True, since it is not expensive....

# Implementation from machinelearningplus.com: Quite slow although it does not check the covariance matrix
print("\nMahalanobis timings for variant from machinelearningplus.com:")
# %timeit mahalanobis_distance_slow(x=X,data=X)

# Using numpy
print("\nMahalanobis Timings for numpy variant 1:")
# %timeit xnp_mahalanobis_distance(X, xnp=np, check_singular=check_singular_cov)

# Using jnp (GPU)
print("\nMahalanobis timings for JAX variant 1:")
# %timeit xnp_mahalanobis_distance(X, xnp=jnp, check_singular=check_singular_cov)

# Using numpy, variant 2
print("\nMahalanobis timings for numpy variant 2:")
# %timeit xnp_mahalanobis_distance2(X, xnp=np, check_singular=check_singular_cov)

# Using jnp (GPU), variant 2
print("\nMahalanobis timings for JAX variant 2:")
# %timeit xnp_mahalanobis_distance2(X, xnp=jnp, check_singular=check_singular_cov)

# Using TensorFlow (GPU)
print("\nMahalanobis timings for TF:")
# %timeit tf_mahalanobis_distance(X, check_singular=check_singular_cov)

print("\nMahalanobis timings for scipy.spatial.distance.mahalanobis():")
# %timeit mahalanobis_distance_scipy(X)

# %%
### Visualize the Mahalanobis distance
import matplotlib.pyplot as plt

X = np.random.multivariate_normal([0, 0], cov, size=5000)
plt.figure(figsize=(12,10))
plt.scatter(X[:,0], X[:,1], c=xnp_mahalanobis_distance(X, xnp=np, check_singular=True), alpha=0.6, cmap="jet")
plt.grid()
plt.colorbar(label="mahalanobis distance")
plt.title("Mahalanobis Distance visualized for a Gaussian-distributed Sample")
plt.show()

# %% [markdown]
# ### Visualize the Whitening Property of the Mahalanobis Distance
# - For further explanations, see appendix below
# - Intuitively, one can imagine that during the computation of the Mahalanobis distance the ellipses (ellipsoids) are transformed into circles (spheres)
# - This is closely related to something called the Whitening Transformation, or in this particular case: Mahalanobis/ZCA whitening
# - The whitening property of the Mahalanobis distance is illustrated in the following:
#
# Further Reading:
# - https://en.wikipedia.org/wiki/Whitening_transformation

# %%
import matplotlib.pyplot as plt

# take the same X as above:
# X = np.random.multivariate_normal([0, 0], cov, size=5000)

# Compute the Whitening matrix: For Explanation, see below
zca = scipy.linalg.sqrtm(np.linalg.inv(cov))
X_white = np.dot(X, zca)

# Now compute the euclidean distance of the whitened data
# We expect that the euclidean distance of the whitened data is the same as the Mahalanobis distance
eucledian_dist = np.linalg.norm(X_white, axis=1, ord=2)
maha_dist = np.sqrt(
    xnp_mahalanobis_distance(X, xnp=np, check_singular=True)
)  # actually, take sqrt here, to get real Mahalanobis dist.

# If you would use the real mean and covariance, the differences between whitened Euclidean distance
# and the Mahalanobis distance would be (nearly) zero. Try uncommenting the following line and see...
# maha_dist = np.sqrt(xnp_mahalanobis_distance(X, xnp=np, mu = [0,0], cov=cov, check_singular=True)) # actually, take sqrt here


# Notice, how the ellipse that we obtained before has changed to a circle and that
# the Euclidean distances of the points to the center of the distribution
# apparently are the same as the Mahalanobis Distance
plt.figure(figsize=(12, 10))
plt.scatter(X_white[:, 0], X_white[:, 1], c=(maha_dist), alpha=0.6, cmap="jet")
plt.grid()
plt.colorbar(label="Mahalanobis distance")
plt.title("ZCA-Whitened Data: Illustration of the Whitening Property of the Mahalanobis Distance")
plt.show()

print(
    "Mean difference of Euclidean distance of ZCA-whitened data & Mahalanobis distances: ",
    np.abs(maha_dist - eucledian_dist).mean(),
)

# %% [markdown]
# #### Visualize 3-dimensional Gaussian

# %%
cov = np.random.rand(3, 3)
cov = np.dot(cov.T, cov)  # positive semidefinite matrix...
X = np.random.multivariate_normal([0, 0, 0], cov, size=5000)


fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(projection="3d")
ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=xnp_mahalanobis_distance(X, xnp=np, check_singular=True), alpha=0.6, cmap="jet")

ax.set_xlabel("X Label")
ax.set_ylabel("Y Label")
ax.set_zlabel("Z Label")
plt.grid()
# plt.colorbar(label="mahalanobis distance")
plt.title("Mahalanobis Distance visualized for a 3-dim Gaussian-distributed Sample")
plt.show()


# %% [markdown]
# ## Example 2: Mahalanobis Distances for high-dimensional Dataset

# %%
matrixSize = 2000
A = np.random.rand(matrixSize, matrixSize)
cov = np.dot(A, A.transpose()) # Create a positive-semidefinite matrix
mean = np.random.rand(matrixSize)
X = np.random.multivariate_normal(mean, cov, size=10000).astype("float32")

# %%
check_singular_cov = True # For small covariance matrices this can be set to True, since it is not expensive....

# Implementation from machinelearningplus.com
print("\nMahalanobis timings for variant from machinelearningplus.com:")
# %timeit mahalanobis_distance_slow(x=X,data=X)

# Using numpy
print("\nMahalanobis Timings for numpy: ")
# %timeit xnp_mahalanobis_distance(X, xnp=np, check_singular=check_singular_cov)

# Using jnp (GPU)
print("\nMahalanobis timings for JAX:")
# %timeit xnp_mahalanobis_distance(X, xnp=jnp, check_singular=check_singular_cov)

# Using numpy, variant 2
print("\nMahalanobis timings for numpy (variant 2):")
# %timeit xnp_mahalanobis_distance2(X, xnp=np, check_singular=check_singular_cov)

# Using jnp (GPU), variant 2
print("\nMahalanobis timings for JAX (variant 2):")
# %timeit xnp_mahalanobis_distance2(X, xnp=jnp, check_singular=check_singular_cov)

# Using TensorFlow (GPU)
print("\nMahalanobis timings for TF:")
# %timeit tf_mahalanobis_distance(X, check_singular=check_singular_cov)

# Using the scipy function
print("\nMahalanobis timings for scipy.spatial.distance.mahalanobis():")
# %timeit mahalanobis_distance_scipy(X)

# %% [markdown]
# ## The (squared) Mahalanobis Distance of a Gaussian-distributed Sample is $\chi^2$-distributed!
# - Discussion can be found below
# - If the assumption can be made that the data is Gaussian, then we can use the quantiles of the $\chi^2$-distribution to compute reasonable "anomaly" thresholds (e.g., using the 99th percentile)
# - If $n$ is the dimensionality of the distribution then the $\chi^2$-distribution has $n$ degrees of freedom

# %%
import numpy as np
import statsmodels.api as sm
import scipy.stats as stats
import pylab as py

# Create sample
matrixSize = 500
A = np.random.rand(matrixSize, matrixSize)
cov = np.dot(A, A.transpose())  # Create a positive-semidefinite matrix
mean = np.random.rand(matrixSize)
X = np.random.multivariate_normal(mean, cov, size=10000)

# Compute squared maha distance
maha_dist = xnp_mahalanobis_distance2(X, xnp=jnp, check_singular=True)

# Quantile-Quantile plot: Ideally, the points are on the 45° line:
fig, ax = plt.subplots(1, figsize=(7, 7))
fig = sm.qqplot(maha_dist, stats.chi2, distargs=(matrixSize,), line="45", ax=ax)
ax.grid()
plt.show()


# %%
# Example for obtaining the 99th percentile
q = 0.99
print(
    f"Real (Empirical) {int(q*100)}-th Percentile of Mahalanobis distance for above sample: ", np.quantile(maha_dist, q)
)
print(f"{int(q*100)}-th percentile of chi2 distribution", scipy.stats.chi2.ppf(q, matrixSize))


# %% [markdown]
# $\def\mclimits_#1{\limits_{\mathclap{#1}}}$
# $\newcommand{\muhat}{{\boldsymbol{\mathbf{{\bar{x}}}}}}$
# $\newcommand{\ehat}{{\boldsymbol{\mathbf{{\bar{e}}}}}}$
# $\newcommand{\bsize}{{\mu}}$
# $\newcommand{\numbatches}{{M}}$
# $\newcommand{\sigmahat}{{\boldsymbol{\mathbf{\bar{\Sigma}}} }}$
# $\newcommand{\bfsigma}{{\boldsymbol{\mathbf{\Sigma}} }}$
# $\newcommand{\xn}{{\boldsymbol{\mathbf{x}}_n}}$
# $\newcommand{\bfx}{{\boldsymbol{\mathbf{x}}}}$
# $\newcommand{\xei}{{\boldsymbol{\mathbf{x}}_i}}$
# $\newcommand{\deltan}{{\boldsymbol{\mathbf{\Delta}}_n}}$
# $\newcommand{\deltai}{{\boldsymbol{\mathbf{\Delta}}_i}}$
# $\newcommand{\bfdelta}{{\boldsymbol{\mathbf{\Delta}}}}$
# $\newcommand{\M}{{\boldsymbol{\mathbf{\bar{M} }}}}$
# $\newcommand{\bfD}{{\boldsymbol{\mathbf{D}}}}$
# $\newcommand{\bfI}{{\boldsymbol{\mathbf{I}}}}$
# $\newcommand{\bfcX}{{\boldsymbol{\mathcal{X}}}}$
#
# ## Incremental/Online-Estimation of (inverse) Covariance Matrix and Mean
# - Can be used in a fully online setting (e.g., on streaming data) to estimate a distribution mean $\muhat_{n}$ and covariance matrix $\sigmahat_n$
# - Advantage: Also estimates the inverse of the covariance matrix fully online without even computing a single matrix inverse
# - incorporates a forgetting factor $\lambda$ which allows to adapt to non-stationary behavior over time
# - If you are operating on infinite data streams, it is recommended to set $\lambda$ to a value slightly smaller than $1$, e.g. $1-1e-8$, to prevent numerical instabilities
# - The memory of the fully online estimator is approximately (shown below in the appendix):
# \begin{align*}
# n_{mem} \approx \frac{1+\lambda}{1-\lambda}.
# \end{align*} Hence, the estimator remembers roughly the last $n_{mem}$ points when computing the mean and covariance.
# - For a more lengthy derivation, see below (appendix)
# - Operational order:
#
# \begin{align}
#  W_n &= \lambda W_{n-1} + 1 \\
#  W_n^{(2)} &= \lambda^2 W_{n-1} + 1 \\
#  \deltan &= \xn - \muhat_{n-1}  \\
#  \muhat_{n} &= \muhat_{n-1} + \frac{\deltan}{W_n} \\
#  \M_{n} &= \lambda \M_{n-1} + \deltan(\xn - \muhat_n)^\tp \label{eq:fully-online-scatter} \\
#  \M_n^{-1} &= \frac{1}{\lambda}\M_{n-1}^{-1} - \frac{\frac{1}{\lambda}\M_{n-1}^{-1}\mathbf\Delta_n(\xn - \muhat_n)^\tp \M_{n-1}^{-1}  }{\lambda + (\xn - \muhat_n)^\tp \M_{n-1}^{-1} \mathbf\Delta_n} \\
#  \sigmahat_n &= \frac{1}{W_n} \M_{n}, \ \ \sigmahat_n^{-1} = {W_n} \M_{n}^{-1} \label{eq:fully-online-sigma} .
# \end{align}
#

# %%
class OnlineCovarianceMeanEstimator:
    """
    It is possible to simply remove (or comment) all references to M̅_n from the
    class to save computation time, if only the inverse covariance matrix is required.
    """

    def __init__(self, xnp, dim, λ):
        self.xnp = xnp
        self.dim = dim
        self.W_n = 0.0
        self.W_n2 = 0.0
        self.λ = λ
        self.x̅_n = self.xnp.zeros((dim, 1), dtype="float64")
        self.M̅_n = self.xnp.zeros((dim, dim), dtype="float64")
        self.M̅_n_inv = self.xnp.eye(dim, dtype="float64") * 1e7

    def get_cov(self):
        """unbiased estimate"""
        return self.M̅_n / (self.W_n - self.W_n2 / self.W_n)

    def get_cov_biased(self):
        return self.M̅_n / self.W_n

    def get_cov_inv(self):
        return self.M̅_n_inv * (self.W_n - self.W_n2 / self.W_n)

    def get_cov_inv_biased(self):
        return self.M̅_n_inv * self.W_n

    def get_mean(self):
        return self.x̅_n.flatten()

    def update(self, x_n):
        x_n = x_n.reshape(self.dim, 1)
        self.W_n = self.λ * self.W_n + 1.0
        self.W_n2 = self.λ**2 * self.W_n2 + 1.0
        Δ_n = x_n - self.x̅_n
        self.x̅_n = self.x̅_n + Δ_n / self.W_n
        Δ_n1 = x_n - self.x̅_n
        self.M̅_n = self.λ * self.M̅_n + self.xnp.dot(Δ_n, Δ_n1.T)

        num = 1.0 / self.λ * self.M̅_n_inv @ Δ_n @ Δ_n1.T @ self.M̅_n_inv
        den = self.λ + Δ_n1.T @ self.M̅_n_inv @ Δ_n
        self.M̅_n_inv = 1.0 / self.λ * self.M̅_n_inv - num / den



# %% [markdown]
# ### Example using the Fully Online Mean-Covariance Estimator

# %%
# Change 0<λ<=1 to values smaller than 1 to introduce some "forgetting" for drift adaptation
ocme = OnlineCovarianceMeanEstimator(xnp=np, dim=2, λ=1)

# Create some sample data
cov = np.array([[3, -3], [-3, 3.5]])
X = np.random.multivariate_normal([1, 2], cov, size=5000)

# Iterate through each example individually
for x in X:
    ocme.update(x)


# %%
# Ensure that the errors are smaller than a given value
error_sigma = np.abs(ocme.get_cov() - np.cov(X.T)).mean()
error_sigma_inv = np.abs(ocme.get_cov_inv() - np.linalg.inv(np.cov(X.T))).mean()
error_mu = np.abs(ocme.get_mean() - X.mean(axis=0)).mean()

print("error_sigma", error_sigma)
print("error_sigma_inv", error_sigma_inv)
print("error_mu", error_mu)
assert error_sigma < 1e-9
assert error_sigma_inv < 1e-9
assert error_mu < 1e-9


# %% [markdown]
# ### Side Experiment: Memory of the Fully Online Mean-Covariance Estimator for $\lambda<1$
#
# $\newcommand{\cov}{{\mbox{cov}}}$
#
# If one selects $\lambda<1$ for the fully-online estimator, the incoming samples are weighted using decaying weights (older examples fade away after some time). Hence, the estimator basically forgets about old examples after a certain number of iterations. However, this implies that the estimated mean & covariance parameters cannot converge to the real values as we process more examples. In other words, the variance in the estimates does not converge to zero for a stationary data-generating distribution. Instead, the variances of the weighted sample mean & weighted covariance matrix will converge to a given non-zero value. If we want to compare our fully-online estimator to the regular sample mean & covariance, which, however, are computed only on the last $n_{mem}$ samples, we can express the memory of the fully-online estimator as follows:
# \begin{align*}
# n_{mem} \approx \frac{1+\lambda}{1-\lambda}.
# \end{align*}
#
# Similar to the standard error of the mean (https://en.wikipedia.org/wiki/Standard_error), one can show that the mean of weighted samples has a a covariance matrix with particular mathmatical expression.
# In general, the covariance of weighted sample means $\bar{X}_n$ and $\bar{Y}_n$ (where $n$ is the sample size) of two random variables $X$ & $Y$ can be written as follows:
#
# \begin{align}
#   \cov(\bar{X}_n,\bar{Y}_n) &= \sum_{i=1}^{n} w_i^2 \cov(X_i,Y_i) \nonumber\\
#  &= \cov(X,Y) \sum_{i=1}^{n} w_i^2, \nonumber
# \end{align}
#
# where $w_i$ are the already normalized weights (unbiased normalization):
# $$
# w_i = \frac{w_i'}{W_n - W_n^{(2)} / W_n}
# $$
#
# Hence, the covariance matrix of the weighted sample mean vector $\muhat$ is:
# \begin{align}
#   \matr \Sigma_{\muhat} = \matr \Sigma \cdot \sum_{i=1}^{n} w_i^2, \nonumber
# \end{align}
#
# This relationship is shown in more detail in the appendix.

# %%
# Create some sample data
def experiment(n_mem, λ, size=500):
    cov = np.array([[3, -3], [-3, 3.5]])
    mu = [1, 2]
    # Generate 10000 examples. We will however see that the OnlineCovarianceMeanEstimator only has
    # a limited memory and "early" examples like X[1] will be forgotten at some point.
    # The question is: What is the memory of the estimator?
    X = np.random.multivariate_normal(mu, cov, size=size)

    ocme = OnlineCovarianceMeanEstimator(xnp=np, dim=2, λ=λ)
    for x in X:
        ocme.update(x)

    # Take the last n_mem points and compute mean & covariance
    mu, cov = X[-n_mem:].mean(axis=0), np.cov(X[-n_mem:].T)

    return np.array([np.concatenate([ocme.get_mean(), ocme.get_cov().flatten()]), np.concatenate([mu, cov.flatten()])])


elem_names = ["$x̅_1$", "$x̅_2$", "$Σ_{1,1}$", "$Σ_{1,2}$", "$Σ_{2,1}$", "$Σ_{2,2}$"]


# %%
lam = 0.99
n_mem = round((1 + lam) / (1 - lam))  # Try your own values here to see how they change the results below
size = 500
n_experiments = 50000  # reduce this number (e.g. to 1000) to get faster results (but not-so-nice histograms)

print(f"Let us assume that the memory of the fully online-estimator with λ={lam} is n_mem={n_mem}")

all_experiments = []
for _ in range(n_experiments):
    all_experiments.append(experiment(n_mem, lam, size))

all_experiments = np.stack(all_experiments)
all_experiments.shape


# %%
# Covariance of the weighted means
w = lam ** np.arange(size)
W = sum(w)
W2 = sum(w**2)
w = w / (W - W2 / W)
expected_Sigma_mean = cov * sum((w) ** 2)
actual_Sigma_mean = np.cov(all_experiments[:, 0, 0:2].T)
print("expected_Sigma_mean:\n", expected_Sigma_mean)
print("\nactual_Sigma_mean:\n", actual_Sigma_mean)
assert np.abs(expected_Sigma_mean - actual_Sigma_mean).mean() < 1e-3


# %%
fig, axs = plt.subplots(2, 3, figsize=(15, 10), constrained_layout=True)
for idx in range(all_experiments.shape[-1]):
    ax_row = idx // 3
    ax_col = idx % 3
    ax = axs[ax_row, ax_col]
    reals = all_experiments[:, 1, idx]
    onlines = all_experiments[:, 0, idx]
    ax.hist(
        reals, label="offline estimator ($n_{mem}=" + str(round(n_mem)) + "$)" if idx < 1 else None, bins=50, alpha=0.5
    )
    ax.hist(onlines, label="online estimator" if idx < 1 else None, bins=50, alpha=0.5)

    mu, sigma = np.mean(reals), np.std(reals)
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.4)
    text_box_str = (
        "$\hat{\mu}_{x̅_{offline}}="
        + str(round(mu, 2))
        + "$\n"
        + "$\hat{\sigma}_{x̅_{offline}}="
        + str(round(sigma, 2))
        + "$"
    )
    ax.text(0.025, 0.95, text_box_str, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    mu, sigma = np.mean(onlines), np.std(onlines)
    text_box_str = (
        "$\hat{\mu}_{x̅_{online}}="
        + str(round(mu, 2))
        + "$\n"
        + "$\hat{\sigma}_{x̅_{online}}="
        + str(round(sigma, 2))
        + "$"
    )
    ax.text(0.7, 0.95, text_box_str, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    if idx < 2:
        std = np.sqrt(expected_Sigma_mean[idx, idx])
        text_box_str = "Expected:\n" + "$\sigma_{x̅_{online}}=" + str(round(sigma, 2)) + "$"
        ax.text(0.7, 0.7, text_box_str, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    ax.set_title(f"Distribution for Estimations of {elem_names[idx]}")

    ax.grid()


fig.legend(loc="upper center", bbox_to_anchor=(0.5, -0.0), fancybox=True, shadow=True, ncol=2)

fig.suptitle(
    "Distributions of the est. parameters $\mathbf{\overline{x}}$ & $\mathbf{\overline{\Sigma}}$ for a forgetting fully-online & a real Estimator using only the last $n_{mem}="
    + str(round(n_mem))
    + "$ samples",
    fontsize=16,
)
plt.show(fig)


# %% [markdown]
# #### Results when (wrongly) assuming that $n_{mem}=100$

# %%
# Do not run this cell, otherwise the plot will be gone!

# %% [markdown]
# ## Batch-incremental of (inverse) Covariance Matrix and Mean
# - **There are still issues with the Estimation of the inverse of the covariance matrix. The estimates are not really reliable. There must be a mistake in the derivation and/or implementation (or numerical issues lead to large deviations)** Hence, for now one should go for the estimate  $\sigmahat_n$ and invert it whenever required.
#
# \begin{align}
# W_{n} &=  \lambda \cdot W_{n-\bsize} + \bsize \\
# W_n^{(2)} &= \lambda^2 \cdot W_{n-\bsize}^{(2)} + \bsize \\
# \deltai &= \xei - \muhat_{n-\bsize} \\
# \muhat_n &=  \muhat_{n-\bsize} + \frac{\sum_{i=k}^{n} \deltai }{W_n} \\
# \bfD_n &= 
# \begin{pmatrix}
# \bfdelta_k &
# \bfdelta_{k+1} &
# \cdots &
# \bfdelta_{n} 
# \end{pmatrix}^\tp \\
# \bfcX_n &= 
# \begin{pmatrix}
# \bfx_k - \muhat_n &
# \bfx_{k+1} - \muhat_n &
# \cdots &
# \bfx_{n} - \muhat_n
# \end{pmatrix}^\tp \\%%%%%%%%%%%%%%%
# \M_{n} &= \lambda \M_{n-\bsize} + \bfD_n^\tp \bfcX_n \\% \sum_{i=k}^{n} \deltai \big(\xei - \muhat_n\big)^\tp \\
# \M_{n}^{-1} &= \frac{1}{\lambda} \M_{n-\bsize}^{-1} - \frac{1}{\lambda} \M_{n-\bsize}^{-1} \bfD_n^\tp 
# \Big(\lambda \bfI + \bfcX_n \M_{n-\bsize}^{-1} \bfD_n^\tp \Big)^{-1} \bfcX_n \M_{n-\bsize}^{-1}\\
# \sigmahat_n &= \frac{\M_{n}}{W_n}, \ \ \sigmahat_n^{-1} = {W_n} \M_{n}^{-1}.
# \end{align}
# where $\bsize$ is the batch size and $k=n-\bsize+1$ is the first index in the new batch.
# Again, for an unbiased estimate of $\sigmahat$ one should either use Eq. \eqref{eq:UnbiasedCovariance1} or Eq. \eqref{eq:UnbiasedCovariance}.
#
# - The Batch-incremental approach actually involves computing a matrix inverse for a $\mu \times \mu$ matrix
# - Note that this algorithm is only faster than the offline approach in estimating the inverse of the covariance matrix, if $\mu < \mbox{dim}(\muhat_n)$. If the batch size is larger than the dimension of the data set, then it only makes sense using this approach, if you cannot process the whole dataset at once in the offline approach

# %%
class BatchCovarianceMeanEstimator:
    """
    It is possible to simply remove (or comment) all references to M̅_n from the
    class to save computation time, if only the inverse covariance matrix is required.
    """

    def __init__(self, xnp, dim, λ):
        self.xnp = xnp
        self.dim = dim
        self.W_n = 0.0
        self.W_n2 = 0.0
        self.λ = λ
        self.x̅_n = self.xnp.zeros((dim, 1), dtype="float64")
        self.M̅_n = self.xnp.zeros((dim, dim), dtype="float64")
        self.M̅_n_inv = xnp.eye(dim)
        self.first = True

    def get_cov(self):
        """unbiased estimate"""
        return self.M̅_n / (self.W_n - self.W_n2 / self.W_n)

    def get_cov_biased(self):
        return self.M̅_n / self.W_n

    def get_cov_inv(self):
        # maybe this multiplication is problematic? probably, big values are multiplied with small ones?
        return self.M̅_n_inv * (self.W_n - self.W_n2 / self.W_n) 

    def get_cov_inv_biased(self):
        return self.M̅_n_inv * self.W_n

    def get_mean(self):
        return self.x̅_n.flatten()

    def update(self, X_n):
        if len(X_n.shape) == 1: X_n = X_n.reshape(self.dim, 1)
        μ = X_n.shape[0]
        
        self.W_n = self.λ * self.W_n + μ
        self.W_n2 = self.λ**2 * self.W_n2 + μ
        Δ_n = X_n - self.x̅_n.T
        self.x̅_n = self.x̅_n + Δ_n.sum(axis=0, keepdims=True).T / self.W_n
        XX_n = X_n - self.x̅_n.T
        self.M̅_n = self.λ * self.M̅_n + Δ_n.T @ XX_n
        
        if self.first:
            self.M̅_n_inv = self.xnp.linalg.inv(self.M̅_n)
            self.first = False
            return
        
        inv = self.xnp.linalg.inv(self.λ * self.xnp.eye(μ) + XX_n @ self.M̅_n_inv @ Δ_n.T)
        self.M̅_n_inv = 1.0 / self.λ * self.M̅_n_inv - 1.0 / self.λ * self.M̅_n_inv @ Δ_n.T @ inv @ XX_n @ self.M̅_n_inv



# %%
# Create some sample data
matrixSize = 300
A = np.random.rand(matrixSize, matrixSize)
cov = np.dot(A, A.transpose()) # Create a positive-semidefinite matrix
mean = np.random.rand(matrixSize)


# Change 0<λ<=1 to values smaller than 1 to introduce some "forgetting" for drift adaptation
ocme = BatchCovarianceMeanEstimator(xnp=np, dim=matrixSize, λ=1)

# Iterate through each example individually
all_X = []
for i in range(1000):
    batch_size = np.random.randint(low=10, high=20)
    X = np.random.multivariate_normal(mean, cov, size=batch_size)
    ocme.update(X)
    all_X.append(X)
    
all_X = np.vstack(all_X)

# %%
# Ensure that the errors are smaller than a given value
error_sigma = np.abs(ocme.get_cov() - np.cov(all_X.T)).mean()
error_sigma_inv = np.abs(ocme.get_cov_inv() - np.linalg.inv(np.cov(all_X.T))).mean()
error_mu = np.abs(ocme.get_mean() - all_X.mean(axis=0)).mean()

print("error_mu", error_mu)
print("error_sigma", error_sigma)
print("error_sigma_inv", error_sigma_inv)

assert error_mu < 1e-9
assert error_sigma < 1e-9
assert error_sigma_inv < 1e-5

# %%

# %%
