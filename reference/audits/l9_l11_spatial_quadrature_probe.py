"""Independent float64 diagnostic, never a rigorous certificate.

Reproduces the spatial normalization/sign of the historical L9-L11 builder;
isolates Gauss-Legendre underintegration without running its expensive arch block.
"""
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss, legvander


def spatial(L, count, degree):
    nodes, weights = leggauss(degree)
    orders = [np.arange(0, 2 * count, 2), np.arange(1, 2 * count, 2)]
    matrices = [np.zeros((count, count)) for _ in orders]
    for n, prime in [(2, 2), (3, 3), (4, 2), (5, 5), (7, 7), (8, 2), (9, 3)]:
        shift = np.log(n)
        if shift >= 2 * L:
            continue
        half = L - shift / 2
        x = shift / 2 + half * nodes
        p1 = legvander(x / L, 2 * count - 1)
        p2 = legvander((x - shift) / L, 2 * count - 1)
        for index, order in enumerate(orders):
            norm = np.sqrt((2 * order + 1) / 2)
            e1 = p1[:, order] * norm
            e2 = p2[:, order] * norm
            overlap = e1.T @ ((half * weights)[:, None] * e2)
            matrices[index] += np.log(prime) / (2 * np.sqrt(n)) * (overlap + overlap.T)
    return matrices


def main():
    results = []
    for L in [np.log(3), 0.5 * np.log(11)]:
        reference = spatial(L, 50, 120)
        for degree in [20, 60, 100, 120]:
            candidate = spatial(L, 50, degree)
            results.append({"L": float(L), "N_sec": 50, "degree": degree,
                            "even_operator_difference_from_120": float(np.linalg.norm(candidate[0] - reference[0], 2)),
                            "odd_operator_difference_from_120": float(np.linalg.norm(candidate[1] - reference[1], 2))})
    output = {"classification": "FLOAT64_DIAGNOSTIC_NOT_CERTIFICATE", "results": results,
              "historical_spatial_normalization_and_sign_preserved": True,
              "archimedean_block_included": False,
              "minimum_polynomial_exact_degree_N50": 100}
    destination = Path(__file__).with_name("L9_L11_SPATIAL_QUADRATURE_PROBE_001.json")
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
