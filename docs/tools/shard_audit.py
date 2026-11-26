"""Audit every shard JUnit ZIP against the planned exact serial test identities."""
import argparse
import json
from pathlib import Path

from regression_evidence import load_report
from shard_plan import validate_plan


def audit(plan, baseline, reports):
    serial, identities = load_report(baseline)
    groups = validate_plan(plan, identities)
    if len(reports) != len(groups):
        raise ValueError("Exactly one report per shard is required")
    seen = set()
    results = []
    clean = not any(serial[k] for k in ("failures", "errors", "skipped"))
    for index, (expected, path) in enumerate(zip(groups, reports)):
        report, actual = load_report(path)
        overlap = seen & actual
        matched = actual == expected
        passed = not any(report[k] for k in ("failures", "errors", "skipped"))
        results.append({"index": index, "sha256": report["sha256"],
                        "tests": report["tests"], "failures": report["failures"],
                        "errors": report["errors"], "skipped": report["skipped"],
                        "missing": len(expected - actual), "unexpected": len(actual - expected),
                        "duplicates_across_shards": len(overlap),
                        "case_seconds": report["case_seconds"]})
        clean = clean and matched and not overlap and passed
        seen.update(actual)
    same = seen == identities
    return {"format": "mano-shard-audit-v1", "baseline_sha256": serial["sha256"],
            "baseline_tests": len(identities), "shards": results,
            "union_matches_baseline": same, "missing_total": len(identities - seen),
            "unexpected_total": len(seen - identities),
            "regression_evidence_clean": clean and same,
            "same_revision_verified": False, "public_release_approved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("reports", nargs="+", type=Path, help="ZIPs in shard-index order")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.plan.read_text(encoding="utf-8")), args.baseline, args.reports)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["regression_evidence_clean"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
