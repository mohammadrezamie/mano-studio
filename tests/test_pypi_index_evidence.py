import pytest
from installer.pypi_index_evidence import check_one

RECORD = {"version":"1.2.3", "url":"https://files.pythonhosted.org/packages/demo.whl", "sha256":"a"*64}

def release():
    return {"info":{"name":"demo","version":"1.2.3"}, "urls":[{"url":RECORD["url"],
            "packagetype":"bdist_wheel","yanked":False,"digests":{"sha256":"a"*64}}]}

def test_exact_index_record():
    assert check_one("demo", RECORD, release())["sha256"] == RECORD["sha256"]

@pytest.mark.parametrize("defect", ["name","version","url","duplicate","type","yanked","sha","missing-yanked"])
def test_reject_inconsistent_index(defect):
    value = release()
    row = value["urls"][0]
    if defect in ("name","version"): value["info"][defect] = "wrong"
    elif defect == "url": row["url"] += ".bad"
    elif defect == "duplicate": value["urls"].append(row.copy())
    elif defect == "type": row["packagetype"] = "sdist"
    elif defect == "yanked": row["yanked"] = True
    elif defect == "sha": row["digests"]["sha256"] = "b"*64
    else: row.pop("yanked")
    with pytest.raises(ValueError):
        check_one("demo", RECORD, value)
