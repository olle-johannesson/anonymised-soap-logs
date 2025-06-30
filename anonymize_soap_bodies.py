#!/usr/bin/env python3
"""
anonymize_fragments.py

Reads XML fragments (e.g. extracted SOAP <Body> blocks) from stdin,
anonymizes PII leaf elements in German locale using Faker,
and writes anonymized XML fragments to stdout.
Maintains a mapping so identical real values map to the same fake.

Usage:
  cat extracted_bodies.xml | python3 anonymize_fragments.py > anonymized.xml
"""
import sys
import re
import xml.etree.ElementTree as ET
from faker import Faker

# Initialize Faker with German locale and mapping cache
faker = Faker('de_DE')
mapping = {}  # (tag_lower, real_val) -> fake_val

# Tags to anonymize (local names, lowercase)
TARGET_TAGS = {
    "firstname", "vorname",
    "lastname", "nachname",
    "dateofbirth", "geburtsdatum",
    "street", "strasse",
    "housenumber", "hausnummer",
    "zipcode", "plz",
    "city", "ort",
    "salutation", "anrede",
    "land", "country",
}

# Regex to remove XML declarations and strip namespace prefixes
DECL_RE   = re.compile(r'<\?xml[^>]*\?>')
PREFIX_RE = re.compile(r'<(/?)[A-Za-z0-9_]+:')


def strip_declarations(text: str) -> str:
    return DECL_RE.sub('', text)


def get_local_name(tag: str) -> str:
    # Remove namespace URI braces
    if tag.startswith('{') and '}' in tag:
        return tag.split('}', 1)[1]
    # Remove prefix before ':'
    if ':' in tag:
        return tag.split(':', 1)[1]
    return tag


def fake_value(tag: str, real: str) -> str:
    key = (tag.lower(), real)
    if key in mapping:
        return mapping[key]
    tl = tag.lower()
    if tl in {"firstname", "vorname"}:
        val = faker.first_name()
    elif tl in {"lastname", "nachname"}:
        val = faker.last_name()
    elif tl in {"dateofbirth", "geburtsdatum"}:
        val = faker.date_of_birth(minimum_age=20, maximum_age=70).isoformat()
    elif tl in {"street", "strasse"}:
        val = faker.street_name()
    elif tl in {"housenumber", "hausnummer"}:
        val = faker.building_number()
    elif tl in {"zipcode", "plz"}:
        val = faker.postcode()
    elif tl in {"city", "ort"}:
        val = faker.city()
    elif tl in {"salutation", "anrede"}:
        val = faker.prefix()
    elif tl in {"land", "country"}:
        val = faker.country()
    else:
        val = real
    mapping[key] = val
    return val


def anonymize_element(elem: ET.Element):
    """Recursively anonymize leaf PII elements in-place."""
    for child in elem:
        anonymize_element(child)
    # If leaf and text present
    if not list(elem) and elem.text and elem.text.strip():
        tag = get_local_name(elem.tag)
        if tag.lower() in TARGET_TAGS:
            elem.text = fake_value(tag, elem.text.strip())


def main():
    # Read all input
    raw = sys.stdin.read()
    if not raw.strip():
        sys.exit(0)
    # Remove XML declarations
    cleaned = strip_declarations(raw)
    # Strip namespace prefixes for parsing
    cleaned = PREFIX_RE.sub(r'<\1', cleaned)
    # Wrap in root to parse multiple fragments
    wrapper = f"<root>{cleaned}</root>"

    try:
        root = ET.fromstring(wrapper)
    except ET.ParseError as e:
        print(f"XML parse error: {e}", file=sys.stderr)
        sys.exit(1)

    # Process each fragment
    for frag in list(root):
        anonymize_element(frag)
        # Serialize fragment back to XML
        out = ET.tostring(frag, encoding='unicode', method='xml')
        print(out)

if __name__ == '__main__':
    main()
