# Compact replacement bridge: how prime-only coupling can become legitimate

Status: candidate conditional lemma, independent review pending. No numerical
tail certificate, interval theorem, or proof of historical truncation constants.

Fix H=L2([-L,L]), an orthogonal projection P onto Legendre degrees0 through d-1,
Q=I-P, and the canonical bounded arithmetic operator V. Suppose a proved
Archimedean floor h(t)>=beta for |t|>=T establishes q_full>=q_H where

    H=beta I+K+V,   K=K_T+K_pole,
    K_T=B* W B,   Bf=F_f restricted to [-T,T] with measure dt/(2pi),
    W=h-beta on [-T,T].

Fourier Plancherel gives ||B||<=1. If ||W||<=M and
E=||Q B*||_HS^2 is bounded, then

    ||K_T-P K_T P|| <= 2||Q K_T|| <= 2M sqrt(E).

The first inequality follows from K_T-PK_TP=QK_T+PK_TQ and self-adjointness.
For the normalized Legendre basis,

    E = integral_-T^T sum_(k>=d) |F_phi_k(t)|^2 dt/(2pi).

Rodrigues' formula and integration by parts give, for real z,
|j_k(z)|<=|z|^k/(2k+1)!!, since |exp(izu)|=1. Therefore

    E <= (2LT/pi) sum_(k>=d) (TL)^(2k)/((2k+1)!!)^2.

Successive majorant ratios are (TL)^2/(2k+3)^2. A partial positive sum
followed by a geometric remainder is rigorous once its ratio is below1.
Large majorants are a certification obstruction, not a negative spectrum.

For real pole vectors c,s with K_pole=2c*c-2s*s (rank-one notation),

    ||K_pole-PK_pole P|| <= 4||c||||Qc||+4||s||||Qs||.

This follows by writing v*v-Pv*(Pv)=Qv*v+Pv*(Qv) and applying the rank-one
norm formula. The pole entry module supplies finite coefficients only;
validated full norms and tail norms are still required here.

If these estimates prove ||K-PKP||<=delta uniformly over a closed L cell,
then H >= H0-delta I with H0=beta I+PKP+V. This LOWER comparison form has
finite block beta I+PKP+PVP-delta I, complement at least

    beta-||V||-delta,

and cross block QVP only. Its full coupling Gram is PVQVP=PV^2P-(PVP)^2.
The Schur component may then use that arithmetic Gram legitimately: compact
coupling has been removed with a proved full operator-norm error, rather than
ignored. A positive finite Schur block and positive complement floor certify
the lower comparison form, hence the original q_full. Every input bound must
be uniform on the same cell and measured in the same orthonormal metric.

This identifies the actual missing link in a prime-only historical Schur
formula. Neither a finite entry error nor a Bessel tail radius labelled
truncation automatically proves the necessary FULL operator-norm delta.
The historical constants have not been authenticated by this argument.
