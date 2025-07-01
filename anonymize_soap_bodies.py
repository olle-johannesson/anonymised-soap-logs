#!/usr/bin/env python3
"""
anonymize_fragments_regex.py

Reads XML from stdin, replaces PII values inside <prefix:Tag>…</prefix:Tag>,
preserving ANY prefix exactly as-is, and writes anonymized XML to stdout.
"""

import sys
import re
from faker import Faker

# Initialize Faker in German locale
faker = Faker('de_DE')

# Keep a mapping so the same real→fake mapping is reused
_mapping = {}

# Tags to anonymize (lowercase local names)
TARGET_TAGS = {
    "firstname","vorname",
    "lastname","nachname",
    "dateofbirth","geburtsdatum",
    "street","strasse",
    "housenumber","hausnummer",
    "zipcode","plz",
    "city","ort",
    "salutation","anrede",
    "land","country",
}

# Build a giant alternation of TARGET_TAGS
tags_re = "|".join(TARGET_TAGS)

# Regex to find <prefix:Tag>value</prefix:Tag>, capturing prefix, tag, value
pattern = re.compile(
    rf"<(?P<prefix>[A-Za-z0-9_]+):(?P<tag>{tags_re})>"
    rf"(?P<val>[^<]+)"
    rf"</(?P=prefix):(?P=tag)>",
    re.IGNORECASE
)

def fake_value(tag: str, real: str) -> str:
    key = (tag.lower(), real)
    if key in _mapping:
        return _mapping[key]

    tl = tag.lower()
    if tl in {"firstname","vorname"}:
        fake = faker.first_name()
    elif tl in {"lastname","nachname"}:
        fake = faker.last_name()
    elif tl in {"dateofbirth","geburtsdatum"}:
        fake = faker.date_of_birth(minimum_age=20, maximum_age=70).isoformat()
    elif tl in {"street","strasse"}:
        fake = faker.street_name()
    elif tl in {"housenumber","hausnummer"}:
        fake = faker.building_number()
    elif tl in {"zipcode","plz"}:
        fake = faker.postcode()
    elif tl in {"city","ort"}:
        fake = faker.city()
    elif tl in {"salutation","anrede"}:
        fake = faker.prefix()
    elif tl in {"land","country"}:
        fake = faker.country()
    else:
        fake = real

    _mapping[key] = fake
    return fake

def repl(m: re.Match) -> str:
    prefix = m.group("prefix")
    tag    = m.group("tag")
    real   = m.group("val")
    fake   = fake_value(tag, real)
    return f"<{prefix}:{tag}>{fake}</{prefix}:{tag}>"

def main():
    xml = sys.stdin.read()
    out = pattern.sub(repl, xml)
    sys.stdout.write(out)

if __name__ == "__main__":
    main()