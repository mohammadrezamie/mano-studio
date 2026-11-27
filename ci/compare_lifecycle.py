"""Compare exact test identity and outcome, then report (not enforce) speed."""
import sys
import xml.etree.ElementTree as ET


def read(path):
    root = ET.parse(path).getroot()
    cases = {}
    for case in root.iter("testcase"):
        key = (case.attrib["classname"], case.attrib["name"])
        if key in cases:
            raise ValueError("Duplicate testcase: " + str(key))
        outcome = next((tag for tag in ("failure", "error", "skipped")
                        if case.find(tag) is not None), "passed")
        cases[key] = (outcome, float(case.attrib["time"]))
    if not cases or any(outcome != "passed" for outcome, _ in cases.values()):
        raise ValueError("Expected nonempty all-passing benchmark")
    return cases


def main():
    old, new = map(read, sys.argv[1:])
    if old.keys() != new.keys():
        raise ValueError("Benchmark test membership differs")
    totals = [sum(time for _, time in cases.values()) for cases in (old, new)]
    print(f"{len(old)} identical passing tests; baseline={totals[0]:.2f}s; cleanup={totals[1]:.2f}s")
    for key in sorted(old, key=lambda k: -old[k][1])[:10]:
        print(f"{key}: {old[key][1]:.3f}s -> {new[key][1]:.3f}s")


if __name__ == "__main__":
    main()
