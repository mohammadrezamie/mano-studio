"""Offline contract tests for the actual workflow script. Never contact GitHub."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/promote-approved-release.yml"
lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
start = lines.index("          python - <<'PY'") + 1
end = lines.index("          PY", start)
SCRIPT = compile("\n".join(x[10:] for x in lines[start:end]), str(WORKFLOW), "exec")
REPO = "mohammadrezamie/mano-studio"
SHA = "a" * 40
DIGEST = "sha256:" + "b" * 64
GATES = ("regression", "installed_payload", "native_acceptance", "security", "redistribution", "corresponding_source", "authenticity", "upgrade")


class PromotionTests(unittest.TestCase):
    def fixture(self, track):
        version, rid, placeholder = {
            "stable": ("1.0.0", 460598745, "untagged-e438c6988649501c973e"),
            "beta": ("1.1.0-beta.1", 460607136, "untagged-786f71ed7a05b8f89b03"),
        }[track]
        tag = "v" + version
        setup = "ManoStudio-Setup-" + tag + "-x64.exe"
        portable = "ManoStudio-" + tag + "-Windows-x64.zip"
        assets = {n: DIGEST for n in (setup, portable, setup+".sha256", portable+".sha256", "qt-source.tar.xz")}
        approval = {"track":track,"version":version,"release_id":rid,"source_sha":SHA,
                    "assets":assets,"corresponding_source_assets":["qt-source.tar.xz"],
                    "automatic_install_approved":False,"authenticode_verified":False,
                    "gates":{g:{"approved":True,"source_sha":SHA,"reviewer":"synthetic fixture",
                                 "evidence":"https://github.com/"+REPO+"/issues/1",
                                 "distribution_sha256":{setup:DIGEST,portable:DIGEST}} for g in GATES}}
        draft = {"id":rid,"draft":True,"prerelease":track=="beta","tag_name":placeholder,
                 "target_commitish":SHA,"assets":[{"name":k,"digest":v} for k,v in assets.items()]}
        return approval, draft, tag

    def execute(self, track="stable", publish=False, change=None, missing=False, tag_exists=False):
        approval, draft, tag = self.fixture(track)
        if change:
            change(approval, draft)
        calls = []
        notes = tag + " SHA-256; unsigned Windows installer."
        def fake_gh(args, **kwargs):
            self.assertEqual(args[:2], ["gh","api"])
            calls.append(args)
            endpoint = args[2]
            if "/commits/" in endpoint:
                return json.dumps({"sha":SHA})
            if "/matching-refs/" in endpoint:
                return json.dumps([{"ref":"refs/tags/"+tag}] if tag_exists else [])
            if args[2:4] == ["--method","PATCH"]:
                self.assertTrue(publish)
                payload = json.loads(Path(args[-1]).read_text())
                self.assertEqual(payload["tag_name"],tag)
                self.assertEqual(payload["target_commitish"],SHA)
                self.assertIs(payload["draft"],False)
                self.assertIs(payload["prerelease"],track=="beta")
                self.assertEqual(payload["make_latest"],"true" if track=="stable" else "false")
                return json.dumps(dict(payload,html_url="synthetic://release"))
            if "/releases/" in endpoint:
                return json.dumps(draft)
            self.fail("Unexpected API call: "+str(args))
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as td:
            try:
                os.chdir(td)
                root = Path("release-approvals")
                root.mkdir()
                if not missing:
                    (root/(track+".json")).write_text(json.dumps(approval))
                (root/(track+"-notes.md")).write_text(notes)
                with patch.dict(os.environ,{"REPO":REPO,"TRACK":track,"PUBLISH":str(publish).lower()},clear=True), patch.object(subprocess,"check_output",side_effect=fake_gh):
                    exec(SCRIPT,{})
            finally:
                os.chdir(previous)
        return calls

    def test_preflight_no_patch(self):
        self.assertTrue(all("--method" not in c for c in self.execute()))
    def test_stable_publication_mock(self):
        self.assertEqual(sum("--method" in c for c in self.execute(publish=True)),1)
    def test_beta_publication_mock(self):
        self.assertEqual(sum("--method" in c for c in self.execute(track="beta",publish=True)),1)
    def test_missing_approval(self):
        with self.assertRaisesRegex(ValueError,"Missing independently reviewed"):
            self.execute(publish=True,missing=True)
    def test_open_security_gate(self):
        with self.assertRaisesRegex(ValueError,"Open or mismatched gate: security"):
            self.execute(publish=True,change=lambda a,d:a["gates"]["security"].update(approved=False))
    def test_changed_asset(self):
        with self.assertRaisesRegex(ValueError,"Draft assets differ"):
            self.execute(publish=True,change=lambda a,d:d["assets"][0].update(digest="sha256:"+"c"*64))
    def test_extra_review_asset(self):
        with self.assertRaisesRegex(ValueError,"Draft assets differ"):
            self.execute(publish=True,change=lambda a,d:d["assets"].append({"name":"OLD-REVIEW-ONLY.exe","digest":DIGEST}))
    def test_existing_tag(self):
        with self.assertRaisesRegex(ValueError,"Tag already exists"):
            self.execute(publish=True,tag_exists=True)
    def test_wrong_channel(self):
        with self.assertRaisesRegex(ValueError,"Not expected private draft"):
            self.execute(publish=True,change=lambda a,d:d.update(prerelease=True))
    def test_no_source(self):
        with self.assertRaisesRegex(ValueError,"Missing approved corresponding-source"):
            self.execute(publish=True,change=lambda a,d:a.update(corresponding_source_assets=[]))
    def test_auto_install_denied(self):
        with self.assertRaisesRegex(ValueError,"must not authorize automatic"):
            self.execute(publish=True,change=lambda a,d:a.update(automatic_install_approved=True))
    def test_wrong_gate_bytes(self):
        with self.assertRaisesRegex(ValueError,"Gate not bound"):
            self.execute(publish=True,change=lambda a,d:a["gates"]["security"].update(distribution_sha256={}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
