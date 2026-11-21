#!/usr/bin/env python3
"""
remediate_all_papers_and_scripts.py

Autonomous remediation script to enforce:
1. Universal Author: Qamar Munawer
2. Universal Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
3. Zero forbidden author strings
4. Presence of lowercase phrase 'ai is being used as a tool' in acknowledgments & .zenodo.json
5. Presence of section 'How Energy, Quantum Matter, Pfaffian Squares, and Real-Life Fields Connect' in all papers
6. Recompilation of PDFs via pdflatex (0 errors)
7. Rebuilding of *_ZENODO.zip archives
8. Mirroring to ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

HODGE_ROOT = Path(r"d:\Comfy UI\hodge conjecture")
SCRIPTS_DIR = HODGE_ROOT / "scripts"
PAPERS_DIR = HODGE_ROOT / "zenodo_theorem_papers"
AUDIT_PAPERS_DIR = Path(r"d:\Comfy UI\ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK\01_hodge_conjecture\papers")

CONNECT_SECTION_TEMPLATE = r"""
\section{How Energy, Quantum Matter, Pfaffian Squares, and Real-Life Fields Connect}

The algebraic and differential identities certified within this framework reflect universal organizing principles shared across algebraic geometry, quantum many-body physics, and field theories:

\begin{enumerate}
  \item \textbf{Curvature Floors and Energy Vacuum Stabilization:} 
  Positive curvature bounds ($k\,\omega - \operatorname{Ric} > 0$ and spectral gap tares $S_{\mathrm{Schur}} \ge \gamma > 0$) function precisely like paramagnetic threshold energies in non-abelian gauge theories. They guarantee that infrared vacuum fluctuations do not destabilize the ground state, establishing strict energy positivity.
  
  \item \textbf{Chiral Splitting and Parity-Protected Degeneracy:} 
  The multiplicity-2 decomposition $2\,Z_{\mathrm{CM}} = P_+ - P_-$ separates opposite chiral sectors, mirroring chiral edge currents and Majorana zero modes in topological superconductors. Symmetrizing across conjugate channels eliminates parity-blind obstructions identically.
  
  \item \textbf{Topological Solitons and Algebraic Cocycle Patching:} 
  Local analytic divisors patch globally via exact cocycle conditions $g_{\alpha\gamma} = g_{\alpha\beta} g_{\beta\gamma}$, corresponding to the absence of Dirac monopoles or gauge anomalies in the fiber bundle formulation of fundamental physical interactions.
  
  \item \textbf{Pfaffian Squares and Microscopic Fermionic Ground States:} 
  Porteous singular loci and determinantal varieties govern phase transitions where Fermi surface topologies change. The non-vanishing of the Pfaffian certifies structural stability against perturbations in both algebraic cycles and physical fermionic ground states.
\end{enumerate}
"""

def update_build_scripts():
    print("--- [1] Updating build scripts ---")
    for script in SCRIPTS_DIR.glob("*.py"):
        try:
            txt = script.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = txt
        # Replace author strings
        txt = re.sub(r'Author:\s*Arqam.*', 'Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg.', txt)
        txt = re.sub(r'\\author\{Arqam.*?\}', r'\\author{Qamar Munawer \\\\ Brandenburg University of Technology Cottbus-Senftenberg}', txt)
        txt = re.sub(r'"name":\s*"Arqam"', '"name": "Qamar Munawer"', txt)
        txt = txt.replace('Brandenburg University of Technology Cottbus-Senftenberg', 'Brandenburg University of Technology Cottbus-Senftenberg')
        txt = txt.replace('', '').replace('', '')
        txt = txt.replace('by Qamar Munawer (Brandenburg University', 'by Qamar Munawer (Brandenburg University')
        txt = txt.replace('Qamar Munawer', 'Qamar Munawer')
        if txt != orig:
            script.write_text(txt, encoding="utf-8")
            print(f"Updated script: {script.name}")

def update_tex_files():
    print("\n--- [2] Updating LaTeX files in zenodo_theorem_papers ---")
    updated_tex = []
    for paper_dir in sorted(PAPERS_DIR.iterdir()):
        if not paper_dir.is_dir():
            continue
        for tex_path in paper_dir.glob("*.tex"):
            txt = tex_path.read_text(encoding="utf-8", errors="ignore")
            orig = txt

            # 1. Author and affiliation
            txt = re.sub(r'\\author\{.*?\}', r'\\author{Qamar Munawer \\\\ Brandenburg University of Technology Cottbus-Senftenberg}', txt, count=1, flags=re.DOTALL)
            txt = txt.replace('Brandenburg University of Technology Cottbus-Senftenberg', 'Brandenburg University of Technology Cottbus-Senftenberg')
            txt = txt.replace('', '').replace('', '')
            txt = re.sub(r'\bArqam\b', 'Qamar Munawer', txt)
            txt = txt.replace('Qamar Munawer (Qamar Munawer)', 'Qamar Munawer')

            # 2. Add Connect Section if missing
            if 'How Energy, Quantum Matter' not in txt:
                # Insert before Conclusion or before Discussion or before Machine-Checked Lean 4
                targets = [r'\section{Machine-Checked Lean 4', r'\section{Numerical Verification', r'\section{Discussion', r'\section{Conclusion', r'\begin{thebibliography}']
                inserted = False
                for tgt in targets:
                    if tgt in txt:
                        txt = txt.replace(tgt, CONNECT_SECTION_TEMPLATE + "\n" + tgt, 1)
                        inserted = True
                        break
                if not inserted:
                    # insert before end document
                    txt = txt.replace(r'\end{document}', CONNECT_SECTION_TEMPLATE + "\n" + r'\end{document}', 1)

            # 3. Ensure lowercase phrase 'ai is being used as a tool'
            if 'ai is being used as a tool' not in txt.lower():
                # Add methodology note before bibliography
                methodology_note = r"""
\section*{Methodology Note}
In this work, ai is being used as a tool to assist in formal verification in Lean~4, symbolic auditing, numerical probing, and manuscript preparation.
"""
                if r'\begin{thebibliography}' in txt:
                    txt = txt.replace(r'\begin{thebibliography}', methodology_note + "\n" + r'\begin{thebibliography}', 1)
                else:
                    txt = txt.replace(r'\end{document}', methodology_note + "\n" + r'\end{document}', 1)

            # Sanitize any stray characters
            txt = txt.replace('·', '.')
            txt = txt.replace('Kähler', 'K\\"ahler')
            txt = txt.replace('Hörmander', 'H\\"ormander')

            if txt != orig:
                tex_path.write_text(txt, encoding="utf-8")
                updated_tex.append(tex_path)
                print(f"Sanitized TeX: {paper_dir.name}/{tex_path.name}")
    return updated_tex

def update_zenodo_json_files():
    print("\n--- [3] Updating .zenodo.json manifests ---")
    for paper_dir in sorted(PAPERS_DIR.iterdir()):
        if not paper_dir.is_dir():
            continue
        zpath = paper_dir / ".zenodo.json"
        if not zpath.exists():
            continue
        try:
            zdata = json.loads(zpath.read_text(encoding="utf-8"))
        except Exception:
            continue
        orig_s = json.dumps(zdata)

        zdata["creators"] = [
            {
                "name": "Qamar Munawer",
                "affiliation": "Brandenburg University of Technology Cottbus-Senftenberg"
            }
        ]
        desc = zdata.get("description", "")
        desc = desc.replace('Brandenburg University of Technology Cottbus-Senftenberg', 'Brandenburg University of Technology Cottbus-Senftenberg')
        desc = desc.replace('', '').replace('', '')
        desc = re.sub(r'\bArqam\b', 'Qamar Munawer', desc)
        if 'ai is being used as a tool' not in desc.lower():
            desc += " In this work, ai is being used as a tool to assist in formal verification, symbol auditing, and manuscript preparation."
        zdata["description"] = desc

        if json.dumps(zdata) != orig_s:
            zpath.write_text(json.dumps(zdata, indent=2), encoding="utf-8")
            print(f"Updated .zenodo.json: {paper_dir.name}")

def compile_pdf(tex_path: Path) -> Path:
    cwd = tex_path.parent
    cmd = ["pdflatex", "-interaction=nonstopmode", tex_path.name]
    for step in range(2):
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
        if res.returncode != 0:
            print(f"[ERROR] pdflatex failed on {tex_path.name} (step {step+1}):")
            if res.stdout:
                lines = res.stdout.splitlines()
                errs = [l for l in lines if l.startswith("!") or "Error" in l]
                print("\n".join(errs[:10]))
            raise RuntimeError(f"pdflatex failed on {tex_path.name}")
    pdf_path = cwd / (tex_path.stem + ".pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not generated: {pdf_path}")
    # clean auxiliary files
    for ext in [".aux", ".log", ".out", ".toc"]:
        aux = cwd / (tex_path.stem + ext)
        if aux.exists():
            try: aux.unlink()
            except Exception: pass
    return pdf_path

def rebuild_zenodo_zip(paper_dir: Path):
    zips = list(paper_dir.glob("*.zip"))
    zip_name = zips[0].name if zips else f"{paper_dir.name}_ZENODO.zip"
    zip_path = paper_dir / zip_name
    all_files = [f for f in paper_dir.iterdir() if f.is_file() and f.suffix not in [".zip", ".aux", ".log", ".out", ".toc"]]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in all_files:
            zf.write(f, arcname=f.name)
    return zip_path

def main():
    update_build_scripts()
    updated_tex = update_tex_files()
    update_zenodo_json_files()

    print(f"\n--- [4] Recompiling PDFs and rebuilding ZIPs for {len(updated_tex)} papers ---")
    AUDIT_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    for tex_path in updated_tex:
        pdir = tex_path.parent
        print(f"\nCompiling {tex_path.name} in {pdir.name}...")
        pdf_path = compile_pdf(tex_path)
        print(f"[OK] Compiled {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
        zip_path = rebuild_zenodo_zip(pdir)
        print(f"[OK] Rebuilt {zip_path.name} ({zip_path.stat().st_size:,} bytes)")

        # Mirror to audit pack
        shutil.copy2(pdf_path, AUDIT_PAPERS_DIR / pdf_path.name)
        shutil.copy2(zip_path, AUDIT_PAPERS_DIR / zip_path.name)
        print(f"[MIRROR] Copied to {AUDIT_PAPERS_DIR / pdf_path.name}")

    print("\n--- [5] ALL PAPERS RECOMPILED & REBUILT CLEANLY ---")

if __name__ == "__main__":
    main()
