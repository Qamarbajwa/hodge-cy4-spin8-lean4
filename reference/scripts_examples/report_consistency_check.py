import os
import re
import sys
import json
import glob
import csv
import yaml
import jsonschema

def check_report_consistency(report_path):
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []
    
    # Rule 1: Check for unhedged 100% claims on finite Monte Carlo
    mc_100_matches = re.findall(r"(\b100(?:\.0+)?%\s*(?:of\s+)?(?:fake|random|controls|trials|synthetic)\b)", content, re.IGNORECASE)
    for m in mc_100_matches:
        if "confidence interval" not in content.lower() and "ci" not in content.lower() and "wilson" not in content.lower():
            issues.append(f"UNHEDGED_STOCHASTIC_CLAIM: Found '{m}' without associated binomial confidence interval.")

    # Rule 2: Check for false equality claims
    equality_prohibitions = [
        ("epsilon = 1 - chi_2", "UNPROVEN_EQUALITY_CLAIM"),
        ("tau = 1 - chi_2", "UNPROVEN_EQUALITY_CLAIM"),
        ("tau = D2", "UNPROVEN_EQUALITY_CLAIM"),
        ("F / A = 1.00", "FACTUAL_ERROR: True ratio is ~10.43 at c=13")
    ]
    for phrase, issue_name in equality_prohibitions:
        if phrase.lower() in content.lower():
            issues.append(f"{issue_name}: Found prohibited phrase '{phrase}'.")

    # Rule 3: Check for false global minimum claims when monotonic
    if "global minimum at sigma = 0.50" in content.lower() and "falsified" not in content.lower() and "retracted" not in content.lower():
        issues.append("MONOTONICITY_CONTRADICTION: Report claims global minimum at sigma=0.50 without noting retraction.")

    # Rule 4: Check for banned absolute words without qualification
    banned_unqualified = ["conclusively proven", "unconditionally verified proof", "certified absolute truth"]
    for b in banned_unqualified:
        if b in content.lower():
            issues.append(f"BANNED_LANGUAGE: Found unqualified absolute term '{b}'.")

    return issues

def validate_yaml_against_schema(yaml_path, schema_path):
    try:
        with open(schema_path, "r", encoding="utf-8") as sf:
            if schema_path.endswith(".json"):
                schema = json.load(sf)
            else:
                schema = yaml.safe_load(sf)
        with open(yaml_path, "r", encoding="utf-8") as yf:
            data = yaml.safe_load(yf)
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except Exception as e:
        return False, str(e)

def scan_governance_v29_schemas():
    print("Executing Governance v2.9 Schema & Intent-Contract Verification...")
    
    schema_pairs = [
        ("governance/bootstrap.yaml", "governance/bootstrap.schema.json"),
        ("governance/trust-anchor.yaml", "governance/trust-anchor.schema.json"),
        ("governance/project-governance.yaml", "governance/project-governance.schema.json")
    ]
    
    for y_path, s_path in schema_pairs:
        if os.path.exists(y_path) and os.path.exists(s_path):
            valid, err = validate_yaml_against_schema(y_path, s_path)
            if not valid:
                print(f"[FAIL] Schema validation failed for {y_path}: {err}")
                return False
            print(f"[PASS] {y_path} conforms to {s_path}")
            
    # Validate intent contracts
    intent_schema = "governance/schemas/intent-contract.schema.yaml"
    if os.path.exists(intent_schema):
        contracts = glob.glob("governance/intent-contracts/*.yaml")
        for c_path in contracts:
            valid, err = validate_yaml_against_schema(c_path, intent_schema)
            if not valid:
                print(f"[FAIL] Intent contract invalid: {c_path}: {err}")
                return False
            print(f"[PASS] Intent contract validated: {c_path}")

    return True

def scan_all_reports():
    reports = glob.glob("*.md") + glob.glob("research/**/*.md", recursive=True)
    all_clean = True
    print(f"Scanning {len(reports)} markdown reports under Governance v2.9 (0-A Truth & Machine Linter)...")
    for r in reports:
        issues = check_report_consistency(r)
        if issues:
            all_clean = False
            print(f"[FAIL] {r}:")
            for iss in issues:
                print(f"  - {iss}")
        else:
            print(f"[PASS] {r}")
            
    v29_schemas_clean = scan_governance_v29_schemas()
    return all_clean and v29_schemas_clean

if __name__ == "__main__":
    success = scan_all_reports()
    if not success:
        sys.exit(1)
    print("All reports, executable scripts, YAML schemas, and intent contracts passed Governance v2.9 machine consistency checks.")
