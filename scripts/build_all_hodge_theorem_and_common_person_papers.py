#!/usr/bin/env python3
"""
build_all_hodge_theorem_and_common_person_papers.py

Generates and compiles individual standalone LaTeX/PDF papers for every
Hodge Conjecture theorem module plus a dedicated common-person relational
explanation paper ("What is happening and what relates to what").
Creates individual .zenodo.json release folders, packages ZIP bundles,
and copies compiled PDFs to the Rosetta Friend Audit Pack.

Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg.
Methodology phrase: "ai is being used as a tool"
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Add script dir to sys.path
sys.path.insert(0, str(Path(__file__).parent))
from hodge_paper_texts import PAPER_00_DATA, HODGE_PAPERS_T

WORKSPACE_ROOT = Path(r"d:\Comfy UI\hodge conjecture")
OUTPUT_DIR = WORKSPACE_ROOT / "zenodo_theorem_papers"
AUDIT_PACK_PAPERS = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK\01_hodge_conjecture\papers")

# Shared LaTeX preamble with scalable Latin Modern fonts
LATEX_HEADER = r"""\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{geometry}
\usepackage{hyperref}

\geometry{
  a4paper,
  top=25mm,
  bottom=25mm,
  left=25mm,
  right=25mm
}

\hypersetup{
  colorlinks=true,
  linkcolor=blue!70!black,
  citecolor=red!70!black,
  urlcolor=teal!70!black
}

\lstdefinelanguage{Lean4}{
  keywords={theorem, lemma, def, structure, where, by, have, exact, refine, intro, rintro, cases, rcases, constructor, calc, ring, norm_num, linarith, nlinarith, omega, dsimp, rw, simpa, import, namespace, end, open},
  keywordstyle=\color{blue!80!black}\bfseries,
  ndkeywords={Prop, Type, Real, Nat, Int, Bool, Set, Matrix, Fin},
  ndkeywordstyle=\color{teal!80!black}\bfseries,
  identifierstyle=\color{black},
  sensitive=true,
  comment=[l]{--},
  morecomment=[s]{/-}{-/},
  commentstyle=\color{green!50!black}\itshape,
  stringstyle=\color{purple},
  basicstyle=\ttfamily\small,
  breaklines=true,
  breakatwhitespace=true,
  frame=single,
  rulecolor=\color{gray!40},
  backgroundcolor=\color{gray!5},
  numbers=none,
  showstringspaces=false
}

\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{remark}[theorem]{Remark}
"""

AUTHOR_BLOCK = r"""\author{Qamar Munawer \\ Brandenburg University of Technology Cottbus-Senftenberg}

\date{\today}
"""

def clean_lean_code_listing(code: str) -> str:
    """Sanitize Lean 4 code for LaTeX listings."""
    subs = {
        '·': '.', '⟨': '<', '⟩': '>', '•': '*', '∧': '/\\',
        '∨': '\\/', '→': '->', '←': '<-', '↔': '<->', '∀': 'forall ',
        '∃': 'exists ', '≤': '<=', '≥': '>=', '≠': '!=', '¬': 'not ',
        'λ': 'fun ', 'α': 'a', 'β': 'b', 'γ': 'c', 'δ': 'd',
        'ε': 'eps', 'θ': 'theta', 'π': 'pi', 'σ': 'sigma',
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
    }
    for k, v in subs.items():
        code = code.replace(k, v)
    return code

def compile_pdf(tex_path: Path) -> Path:
    """Compile LaTeX file to PDF using pdflatex twice."""
    cwd = tex_path.parent
    cmd = ["pdflatex", "-interaction=nonstopmode", tex_path.name]
    for step in range(2):
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
        if res.returncode != 0:
            print(f"Error compiling {tex_path.name} on pass {step+1}:")
            out_sample = res.stdout[-1500:] if res.stdout else "No stdout"
            print(out_sample)
            raise RuntimeError(f"pdflatex failed on {tex_path.name}")
    pdf_path = cwd / (tex_path.stem + ".pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected output PDF not found: {pdf_path}")
    print(f"[OK] Compiled: {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
    return pdf_path

def write_zenodo_json(folder: Path, title: str, description: str, keywords: list[str]):
    """Write dedicated .zenodo.json manifest."""
    zdata = {
        "title": title,
        "description": description + " In this work, ai is being used as a tool to assist in formal verification, symbol auditing, and manuscript preparation.",
        "creators": [
            {
                "name": "Qamar Munawer",
                "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"
            }
        ],
        "keywords": keywords + ["Hodge Conjecture", "Lean 4", "Formal Verification", "Calabi-Yau 4-folds"],
        "license": "CC-BY-4.0",
        "upload_type": "publication",
        "publication_type": "article",
        "access_right": "open"
    }
    (folder / ".zenodo.json").write_text(json.dumps(zdata, indent=2), encoding="utf-8")

def clean_aux_files(folder: Path):
    """Remove auxiliary LaTeX build files."""
    for ext in [".aux", ".log", ".out", ".toc"]:
        for f in folder.glob(f"*{ext}"):
            try:
                f.unlink()
            except Exception:
                pass

def create_bundle_zip(folder: Path, zip_name: str):
    """Package folder contents into a clean release ZIP."""
    clean_aux_files(folder)
    zip_path = folder / zip_name
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in folder.iterdir():
            if f.is_file() and f.suffix in [".pdf", ".tex", ".lean", ".py", ".json"] and f.name != zip_name:
                zf.write(f, arcname=f.name)
    print(f"[ZIP] Created {zip_path.name} ({zip_path.stat().st_size:,} bytes)")

def sanitize_latex(text: str) -> str:
    """Sanitize LaTeX text to eliminate problematic Unicode in listings and text."""
    text = text.replace('·', '.')
    text = text.replace('Kähler', 'K\\"ahler')
    return text

def build_paper_00() -> Path:
    """Build Paper 00: The Common-Person Relational Master Guide."""
    folder = OUTPUT_DIR / PAPER_00_DATA["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    tex_path = folder / f"{PAPER_00_DATA['filename']}.tex"

    doc = LATEX_HEADER + f"""
\\title{{\\textbf{{{PAPER_00_DATA['title']}}}}}
""" + AUTHOR_BLOCK + r"""
\begin{document}

\maketitle

\begin{abstract}
""" + PAPER_00_DATA["abstract"] + r"""
\end{abstract}

\vspace{1em}
\noindent\textbf{Keywords:} """ + ", ".join(PAPER_00_DATA["keywords"]) + r"""

""" + PAPER_00_DATA["body"] + r"""

\begin{thebibliography}{99}
\bibitem{Hodge1950} W.~V.~D.~Hodge, \emph{The Topological Invariants of Algebraic Varieties}, Proceedings of the International Congress of Mathematicians, Cambridge, Mass., Vol. 1, pp. 182--192, 1950.
\bibitem{Deligne1971} P.~Deligne, \emph{Th\'eorie de Hodge II}, Publications Math\'ematiques de l'IH\'ES, Vol. 40, pp. 5--57, 1971.
\bibitem{KugaSatake1967} M.~Kuga and I.~Satake, \emph{Abelian Varieties Attached to Polarized $K3$ Surfaces}, Mathematische Annalen, Vol. 169, pp. 239--242, 1967.
\bibitem{Griffiths1968} P.~A.~Griffiths, \emph{Periods of Integrals on Algebraic Manifolds: Summary of Main Results and Discussion of Open Problems}, Bulletin of the American Mathematical Society, Vol. 76, pp. 228--296, 1970.
\bibitem{Voisin2002} C.~Voisin, \emph{Hodge Theory and Complex Algebraic Geometry I \& II}, Cambridge Studies in Advanced Mathematics, Cambridge University Press, 2002.
\end{thebibliography}

\end{document}
"""
    doc = sanitize_latex(doc)
    tex_path.write_text(doc, encoding="utf-8")
    pdf_path = compile_pdf(tex_path)

    # Copy key Lean certs to Paper 00 folder
    certs = [
        "examples/math_gov/LeanMillenniumExt/CliffordKugaSatakeSchurExt.lean",
        "examples/math_gov/LeanMillenniumExt/SchurUniversalSp8ProjectionExt.lean",
        "examples/math_gov/LeanMillenniumExt/MumfordCMSpecializationCycleExt.lean",
        "dist/zenodo_verified_deposit_v1.0/HodgeClayConditionsStage1to3Cert.lean",
        "examples/math_gov/LeanMillenniumExt/HodgeArakelovBostDegreeCompactnessCert.lean"
    ]
    for c in certs:
        src = WORKSPACE_ROOT / c
        if src.exists():
            shutil.copy2(src, folder / src.name)

    write_zenodo_json(folder, PAPER_00_DATA["title"], PAPER_00_DATA["abstract"], PAPER_00_DATA["keywords"])
    create_bundle_zip(folder, f"{PAPER_00_DATA['folder']}_ZENODO.zip")
    return pdf_path

def build_theorem_paper(pdata: dict) -> Path:
    """Build an individual theorem paper."""
    folder = OUTPUT_DIR / pdata["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    tex_path = folder / f"{pdata['filename']}.tex"

    doc = LATEX_HEADER + f"""
\\title{{\\textbf{{{pdata['title']}}}}}
""" + AUTHOR_BLOCK + r"""
\begin{document}

\maketitle

\begin{abstract}
""" + pdata["abstract"] + r"""
\end{abstract}

\vspace{1em}
\noindent\textbf{Keywords:} """ + ", ".join(pdata["keywords"]) + r"""

""" + pdata["body"] + r"""

\begin{thebibliography}{99}
\bibitem{Hodge1950} W.~V.~D.~Hodge, \emph{The Topological Invariants of Algebraic Varieties}, Proceedings of the International Congress of Mathematicians, Cambridge, Mass., Vol. 1, pp. 182--192, 1950.
\bibitem{Deligne1971} P.~Deligne, \emph{Th\'eorie de Hodge II}, Publications Math\'ematiques de l'IH\'ES, Vol. 40, pp. 5--57, 1971.
\bibitem{KugaSatake1967} M.~Kuga and I.~Satake, \emph{Abelian Varieties Attached to Polarized $K3$ Surfaces}, Mathematische Annalen, Vol. 169, pp. 239--242, 1967.
\bibitem{Bost1996} J.-B.~Bost, \emph{P\'eriodes et degr\'es des sous-vari\'et\'es ab\'eliennes}, Institut des Hautes \'Etudes Scientifiques, 1996.
\bibitem{Voisin2002} C.~Voisin, \emph{Hodge Theory and Complex Algebraic Geometry}, Cambridge University Press, 2002.
\end{thebibliography}

\end{document}
"""
    doc = sanitize_latex(doc)
    tex_path.write_text(doc, encoding="utf-8")
    pdf_path = compile_pdf(tex_path)

    # Copy lean source
    if "lean_src" in pdata:
        lsrc = WORKSPACE_ROOT / pdata["lean_src"]
        if lsrc.exists():
            shutil.copy2(lsrc, folder / lsrc.name)
        else:
            # Check standalone papers dir
            alt = WORKSPACE_ROOT / "zenodo_standalone_papers"
            matches = list(alt.rglob(Path(pdata["lean_src"]).name))
            if matches:
                shutil.copy2(matches[0], folder / matches[0].name)

    # Copy probe source
    if "probe_src" in pdata:
        psrc = Path(pdata["probe_src"])
        if not psrc.is_absolute():
            psrc = WORKSPACE_ROOT / psrc
        if psrc.exists():
            shutil.copy2(psrc, folder / psrc.name)
        else:
            # Check audit pack
            alt = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK\01_hodge_conjecture\probes")
            p_alt = alt / Path(pdata["probe_src"]).name
            if p_alt.exists():
                shutil.copy2(p_alt, folder / p_alt.name)

    write_zenodo_json(folder, pdata["title"], pdata["abstract"], pdata["keywords"])
    create_bundle_zip(folder, f"{pdata['folder']}_ZENODO.zip")
    return pdf_path

def main():
    print("=" * 78)
    print("STARTING HODGE THEOREM & COMMON-PERSON PAPERS GENERATION & COMPILATION")
    print("=" * 78)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_PACK_PAPERS.mkdir(parents=True, exist_ok=True)

    compiled_pdfs = []

    # 1. Build Paper 00 (Common-Person Relational Guide)
    print("\n[01/09] Building Paper 00: Common-Person Relational Guide...")
    pdf00 = build_paper_00()
    compiled_pdfs.append(pdf00)

    # 2. Build Theorem Papers T01 to T08
    for idx, pdata in enumerate(HODGE_PAPERS_T, start=2):
        print(f"\n[{idx:02d}/09] Building {pdata['id']}...")
        pdf_thm = build_theorem_paper(pdata)
        compiled_pdfs.append(pdf_thm)

    # 3. Mirror all compiled PDFs into Rosetta Friend Audit Pack
    print("\n" + "=" * 78)
    print("MIRRORING ALL 9 COMPILED PDFS TO ROSETTA FRIEND AUDIT PACK")
    print("=" * 78)
    for pdf in compiled_pdfs:
        dest = AUDIT_PACK_PAPERS / pdf.name
        shutil.copy2(pdf, dest)
        print(f"[MIRROR] Copied {pdf.name} to {dest}")

    # 4. Write Master Receipt
    receipt = {
        "status": "PASS",
        "total_papers_built": len(compiled_pdfs),
        "papers": [
            {
                "name": p.name,
                "size_bytes": p.stat().st_size,
                "path": str(p.resolve())
            }
            for p in compiled_pdfs
        ]
    }
    receipt_path = OUTPUT_DIR / "HODGE_9_PAPERS_BUILD_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"\n[RECEIPT] Master receipt saved to {receipt_path}")
    print("=" * 78)
    print("ALL 9 HODGE PAPERS GENERATED, COMPILED, AND PACKAGED SUCCESSFULLY!")
    print("=" * 78)

if __name__ == "__main__":
    main()
