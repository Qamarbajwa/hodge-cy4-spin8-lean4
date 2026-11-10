# Cost sensitivity of the sufficient compact bound

Executed at L<=23/20,T=400 with SUPPLIED, NOT VALIDATED symbol supremum M=10.
The conditional norm majorant gives approximately2.16e100 for degree cutoff100,
1.45e77 for400,2.13e-12 for650,and8.30e-36 for700. Exact rational outputs are
preserved in COMPACT_TAIL_COST_RECEIPT.json; floats are display diagnostics only.

This measures a crude sufficient majorant, not true spectral deterioration or
the actual truncation error. The real-argument Rodrigues bound |j_k(z)|<=
z^k/(2k+1)!! ignores oscillatory cancellation. A tiny majorant is achievable
at a large degree, but a full700-dimensional exact rational LDL could be costly.
Sharper verified Bessel estimates or compact-kernel low-rank approximations
therefore deserve priority before inflating every matrix indiscriminately.

One diagnostic export hit Python's4300-digit integer-string guard; that is a
serialization limitation, not a failed mathematical inequality. The local
export used an explicit50000-digit cap; source checker and reviewed theorem
were unchanged. No supplied M, pole tail, complement or spectral positivity
was authenticated by this cost experiment. Restored intervals remain0.
