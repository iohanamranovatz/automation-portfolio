import contextlib
import hashlib
import json
import platform
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import allure

REPORTS_DIR = Path("reports/bugs")
SEVERITY_ORDER = ["critical", "major", "minor", "trivial"]


class BugFound(AssertionError):
    """Assert cu expected/actual separate, ca să ajungă curat în bug report."""

    def __init__(self, expected: str, actual: str):
        self.expected, self.actual = expected, actual
        super().__init__(f"Expected: {expected}\nActual: {actual}")


def check(condition: bool, expected: str, actual: str):
    if not condition:
        raise BugFound(expected, actual)


class StepRecorder:
    """Ține minte pașii testului: devin 'Steps to reproduce' în raport și apar și în Allure."""

    def __init__(self):
        self.steps: list[str] = []

    @contextlib.contextmanager
    def __call__(self, description: str):
        self.steps.append(description)
        with allure.step(description):
            yield


@dataclass
class BugReport:
    id: str
    title: str
    severity: str
    test: str
    steps: list[str]
    expected: str
    actual: str
    environment: dict
    url: str | None = None
    screenshot: str | None = None
    console_errors: list[str] = field(default_factory=list)
    found_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_markdown(self) -> str:
        steps = "\n".join(f"{i}. {s}" for i, s in enumerate(self.steps, 1)) or "_(fără pași înregistrați)_"
        env = "\n".join(f"- **{k}:** {v}" for k, v in self.environment.items())
        md = [
            f"# {self.id}: {self.title}",
            "",
            f"**Severity:** {self.severity}  ",
            f"**Status:** New - needs triage  ",
            f"**Found at:** {self.found_at}  ",
            f"**Automated test:** `{self.test}`",
            "",
            "## Steps to reproduce",
            steps,
            "",
            "## Expected result",
            self.expected,
            "",
            "## Actual result",
            self.actual,
            "",
            "## Environment",
            env,
        ]
        if self.url:
            md += ["", f"**URL at failure:** {self.url}"]
        if self.console_errors:
            md += ["", "## Console errors", "```", *self.console_errors, "```"]
        if self.screenshot:
            md += ["", "## Screenshot", f"![screenshot]({self.screenshot})"]
        return "\n".join(md) + "\n"


def bug_id(nodeid: str) -> str:
    # același test -> același ID la fiecare rulare, ca să poți urmări bug-ul în timp
    return "BUG-" + hashlib.sha1(nodeid.encode()).hexdigest()[:6].upper()


def reset_reports_dir():
    shutil.rmtree(REPORTS_DIR, ignore_errors=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save(report: BugReport, screenshot_png: bytes | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if screenshot_png:
        report.screenshot = f"{report.id}.png"
        (REPORTS_DIR / report.screenshot).write_bytes(screenshot_png)
    (REPORTS_DIR / f"{report.id}.json").write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    path = REPORTS_DIR / f"{report.id}.md"
    path.write_text(report.to_markdown())
    return path


def write_index():
    bugs = [json.loads(p.read_text()) for p in REPORTS_DIR.glob("BUG-*.json")]
    bugs.sort(key=lambda b: (SEVERITY_ORDER.index(b["severity"]) if b["severity"] in SEVERITY_ORDER else 99, b["title"]))
    lines = [f"# Bug reports ({len(bugs)})", "",
             f"Generated: {datetime.now().isoformat(timespec='seconds')} on {platform.system()}", "",
             "| ID | Severity | Title | Test |", "|---|---|---|---|"]
    lines += [f"| [{b['id']}]({b['id']}.md) | {b['severity']} | {b['title']} | `{b['test']}` |" for b in bugs]
    (REPORTS_DIR / "index.md").write_text("\n".join(lines) + "\n")
