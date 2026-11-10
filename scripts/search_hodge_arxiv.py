import subprocess
import json

cmd = [
    r"C:\Users\arqam\.gemini\config\plugins\science\skills\literature_search_arxiv\scripts\search_arxiv.py",
    "--query",
    'ti:"Hodge conjecture"',
    "--max_results",
    "10",
]

res = subprocess.run(["uv", "run"] + cmd, capture_output=True, text=True, encoding="utf-8")
out = res.stdout.strip()

# parse last JSON object
idx = out.rfind('{\n  "status": "success"')
if idx != -1:
    data = json.loads(out[idx:])
    print(f"Total retrieved: {len(data.get('papers', []))}")
    for p in data.get("papers", []):
        print(f"[{p['id']}] {p['title']} ({p.get('published', '')[:4]})")
        print(f"  Authors: {', '.join(p.get('authors', []))}")
        print(f"  PDF: {p.get('pdf_url', '')}")
else:
    print("Error / Raw output:")
    print(out[:500])
