import glob
import re
import os

scripts = sorted(glob.glob('scripts/verify_l*_coercive_interval_stability_001.py'))
print(f"Total verifiers found: {len(scripts)}")
for s in scripts:
    name = os.path.basename(s)
    with open(s, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # N_sec
    m_nsec = re.search(r'N_sec\s*=\s*(\d+)', content)
    nsec = m_nsec.group(1) if m_nsec else '?'
    
    # T_sharp
    m_t = re.search(r'T_sharp\s*=\s*(\d+)', content)
    t_val = m_t.group(1) if m_t else '?'
    
    # Probes
    probes = re.findall(r'\"probe\":\s*([^,\n}]+)', content)
    probes_alt = re.findall(r'falsification_results\.append\(', content)
    num_probes = max(len(probes), len(probes_alt))
    hardcoded = len(re.findall(r'p\d+\s*=\s*\"PASS', content))
    
    # Recompute / fixture
    has_recompute = '--recompute' in content
    has_fixture = 'DEFAULT_FIXTURE_EIGENVALUES' in content
    
    # Task ID / Interval
    m_task = re.search(r'RH-CCM-([A-Z0-9\-]+)-COERCIVE', content)
    task_id = m_task.group(0) if m_task else '?'
    
    print(f"{name:50s} | {task_id[:35]:35s} | N={nsec:>3} | T={t_val:>7} | probes={num_probes:>2} | hardcoded={hardcoded:>2} | fix={str(has_fixture):<5} | rec={str(has_recompute):<5}")
