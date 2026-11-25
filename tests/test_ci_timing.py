import subprocess
import sys
from pathlib import Path

import pytest
from dev_tools.ci_timing import Case, read_cases, report


@pytest.fixture
def junit(tmp_path):
    path = tmp_path / 'result.xml'
    path.write_text('''<testsuites><testsuite>
<testcase classname="test_a" name="fast" time="0.5"/>
<testcase classname="test_a" name="slow" time="3"><failure>not copied</failure></testcase>
<testcase classname="test_b" name="broken" time="1"><error/></testcase>
<testcase classname="test_b" name="skip" time="0"><skipped/></testcase>
</testsuite></testsuites>''', encoding='utf-8')
    return path


def test_summary_and_order(junit):
    cases = read_cases(junit)
    assert [c.outcome for c in cases] == ['passed', 'failure', 'error', 'skipped']
    output = report(cases)
    assert 'Cases: 4 · passed: 1 · failed: 1 · errors: 1 · skipped: 1' in output
    assert '4.500 s' in output
    assert '| test_a | 2 | 3.500 | 77.8% |' in output
    assert output.index('test_a::slow') < output.index('test_b::broken') < output.index('test_a::fast')
    assert 'not copied' not in output


def test_ties_limit_and_escaping():
    cases = [Case('z', 'a', 2, 'passed'), Case('a', '<tag>|`', 2, 'passed')]
    text = report(cases, 1)
    assert '| a | 1 | 2.000 | 50.0% |' in text
    assert 'a::&lt;tag&gt;&#124;&#96;' in text
    assert 'z::a' not in text
    assert '0.0%' in report([Case('zero', 'x', 0, 'passed')])
    assert 'Cases: 0' in report([])
    with pytest.raises(ValueError):
        report(cases, 0)


@pytest.mark.parametrize('duration', ['-1', 'nan', 'inf', 'bad'])
def test_invalid_duration(tmp_path, duration):
    p = tmp_path / 'result.xml'
    p.write_text(f'<testsuite><testcase time="{duration}"/></testsuite>')
    with pytest.raises(ValueError):
        read_cases(p)


def test_cli_and_step_summary(junit, tmp_path, monkeypatch):
    summary = tmp_path / 'summary.md'
    output = tmp_path / 'report' / 'timings.md'
    summary.write_text('Prior step\n')
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    script = Path(__file__).resolve().parents[1] / 'dev_tools' / 'ci_timing.py'
    result = subprocess.run([sys.executable, str(script), str(junit), '--output', str(output)], capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert summary.read_text(encoding='utf-8') == 'Prior step\n' + output.read_text(encoding='utf-8')
    bad = subprocess.run([sys.executable, str(script), str(tmp_path / 'missing.xml'), '--output', str(output)], capture_output=True, timeout=15)
    assert bad.returncode != 0 and b'Timing report error' in bad.stderr
