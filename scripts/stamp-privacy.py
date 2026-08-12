#!/usr/bin/env python3
"""Set the privacy policy's "Last Updated" date and stamp what it refers to.

The date sat at "July 27, 2026" on the day the policy's definition of the User
ID was corrected, a Device ID entry was added, and video calling was removed
from it. Nothing was dishonest on purpose — a date maintained by hand simply
does not move on its own, and this one is the kind that matters: a privacy
policy whose "last updated" is wrong misstates when users were told something.

So it is derived, not remembered. This script writes today's date into every
locale and records a hash of the policy text alongside it; `check-i18n.py`
recomputes that hash and fails when the text has moved and the date has not.
The date field itself is excluded from the hash, or it could never settle.

    python3 scripts/stamp-privacy.py              # stamp with today's date
    python3 scripts/stamp-privacy.py 2026-08-12   # stamp with a specific date
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ("en", "ru", "ja")
DATE_KEY = "privacy.privacy-policy.p2"
STAMP = ROOT / "scripts/.privacy-stamp"

RU_MONTHS = ("января", "февраля", "марта", "апреля", "мая", "июня",
             "июля", "августа", "сентября", "октября", "ноября", "декабря")


def policy_hash() -> str:
    """Hash every privacy.* string in every locale, except the date line."""
    h = hashlib.sha256()
    for lang in LANGS:
        d = json.loads((ROOT / f"i18n/{lang}.json").read_text(encoding="utf-8"))
        for key in sorted(k for k in d if k.startswith("privacy.") and k != DATE_KEY):
            h.update(key.encode() + b"\x00" + d[key].encode() + b"\x00")
    return h.hexdigest()[:12]


def render(lang: str, day: dt.date) -> str:
    if lang == "ru":
        return (f"Последнее обновление: {day.day} {RU_MONTHS[day.month - 1]} {day.year}"
                f"  ·  Вступила в силу: 4 марта 2026")
    return (f"Last Updated: {day.strftime('%B')} {day.day}, {day.year}"
            f"  ·  Effective Date: March 4, 2026")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    day = dt.date.fromisoformat(args[0]) if args else dt.date.today()

    for lang in LANGS:
        fp = ROOT / f"i18n/{lang}.json"
        d = json.loads(fp.read_text(encoding="utf-8"))
        d[DATE_KEY] = render(lang, day)
        fp.write_text(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")

    # The English string is also the no-JS fallback in the markup.
    page = ROOT / "privacy.html"
    text = page.read_text(encoding="utf-8")
    fallback = render("en", day).replace("  ·  ", " &nbsp;·&nbsp; ")
    text, n = re.subn(r'(data-i18n="privacy\.privacy-policy\.p2">)[^<]*(</p>)',
                      lambda m: m.group(1) + fallback + m.group(2), text, count=1)
    if not n:
        return print("privacy.html: date fallback not found") or 1
    page.write_text(text, encoding="utf-8")

    STAMP.write_text(f"{day.isoformat()} {policy_hash()}\n", encoding="utf-8")
    print(f"privacy policy stamped {day.isoformat()} ({policy_hash()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
