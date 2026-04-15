"""Secret / credential scanner.

Scans file source text for common secret patterns (API keys, tokens, private
keys, database URLs, etc.) and returns human-readable warning strings.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

# ── Pattern registry ────────────────────────────────────────────────────────────

class _Pattern(NamedTuple):
    label: str
    regex: re.Pattern[str]


_PATTERNS: list[_Pattern] = [
    # AWS
    _Pattern("AWS access key",      re.compile(r"(?<![A-Z0-9])(AKIA[0-9A-Z]{16})(?![A-Z0-9])")),
    _Pattern("AWS secret key",      re.compile(r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]")),
    # GitHub / GitLab
    _Pattern("GitHub token",        re.compile(r"(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})")),
    _Pattern("GitLab token",        re.compile(r"glpat-[A-Za-z0-9\-_]{20}")),
    # Private keys
    _Pattern("Private key header",  re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    # Stripe
    _Pattern("Stripe secret key",   re.compile(r"sk_(live|test)_[0-9a-zA-Z]{24,}")),
    _Pattern("Stripe publishable",  re.compile(r"pk_(live|test)_[0-9a-zA-Z]{24,}")),
    # Slack
    _Pattern("Slack token",         re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}")),
    # Twilio
    _Pattern("Twilio account SID",  re.compile(r"AC[0-9a-f]{32}")),
    _Pattern("Twilio auth token",   re.compile(r"(?i)twilio.{0,20}['\"][0-9a-f]{32}['\"]")),
    # JWT
    _Pattern("JWT token",           re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    # Database URLs with credentials
    _Pattern("DB connection string", re.compile(
        r"(?i)(postgres|mysql|mongodb|redis|amqp|ftp)://[^:@\s]+:[^@\s]+@[^\s\"']+"
    )),
    # Generic high-entropy assignments (last resort — low specificity)
    _Pattern("Hardcoded password",  re.compile(
        r"(?i)(?:password|passwd|pwd|secret|api_key|apikey|auth_token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    )),
    # Google API key
    _Pattern("Google API key",      re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    # Heroku API key
    _Pattern("Heroku API key",      re.compile(r"[hH]eroku[^0-9a-f]?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")),
    # SendGrid
    _Pattern("SendGrid API key",    re.compile(r"SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}")),
    # npm auth token
    _Pattern("npm auth token",      re.compile(r"//registry\.npmjs\.org/:_authToken=[A-Za-z0-9\-]+")),
]

# Extensions whose files should be skipped entirely (binaries, lock files, etc.)
_SKIP_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp",
    ".mp3", ".mp4", ".wav", ".ogg", ".flac",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".woff", ".woff2", ".ttf", ".eot",
    ".lock", ".sum",
})

# Files whose names suggest they already ARE secret storage — skip
_SKIP_FILENAMES = frozenset({
    ".env", ".env.local", ".env.development", ".env.production",
    ".env.example",  # example files are fine, but still skip scan
    "secrets.json", "credentials.json",
})


def scan_secrets(path: Path, src: str) -> list[str]:
    """Return a list of warning strings if secrets are detected in *src*.

    Each warning is a human-readable string suitable for display in the
    dashboard's architectural-warnings section.
    """
    if path.suffix.lower() in _SKIP_EXTENSIONS:
        return []
    if path.name in _SKIP_FILENAMES:
        return []

    found: list[str] = []
    seen_labels: set[str] = set()

    lines = src.splitlines()
    for lineno, line in enumerate(lines, 1):
        # Skip obvious comment lines
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--")):
            continue
        for pat in _PATTERNS:
            if pat.label in seen_labels:
                continue
            if pat.regex.search(line):
                found.append(f"Possible secret detected: {pat.label} (line {lineno})")
                seen_labels.add(pat.label)

    return found
