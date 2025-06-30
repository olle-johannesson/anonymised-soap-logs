#!/usr/bin/env python3
"""
Anonymize SOAP body XML by replacing PII fields (like name/address)
with consistent fake values using a replacement dictionary.
"""

import sys
import re
import xml.etree.ElementTree as ET
from faker import Faker
from collections import defaultdict

# Fields to anonymize, with partial tag matching
TARGET_TAGS = {
    "LastName",
    "FirstName",
    "DateOfBirth",
    "Street",
    "HouseNumber",
    "ZipCode",
    "City"
}

faker = Faker()
mapping = defaultdict(str)

def fake_value(tag, real_val):
    """Generate or reuse a fake value for the given tag + real value."""
    key = f"{tag}|{real_val.strip()}"
    if mapping[key]:
        return mapping[key]

    match tag:
        case "FirstName":
            val = faker.first_name()
        case "LastName":
            val = faker.last_name()
        case "Street":
            val = faker.street_name()
        case "HouseNumber":
            val = str(faker.building_number())
        case "City":
            val = faker.city()
        case "ZipCode":
            val = faker.postcode()
        case "DateOfBirth":
            val = faker.date_of_birth(minimum_age=20, maximum_age=70).isoformat()
        case _:
            val = "REDACTED"

    mapping[key] = val
    return val

def anonymize(xml_str):
    try:
        root = ET.fromstring(f"<wrap>{xml_str}</wrap>")
        for elem in root.iter():
            tag = elem.tag.split(":")[-1]  # strip namespace prefix
            if tag in TARGET_TAGS and elem.text and elem.text.strip():
                elem.text = fake_value(tag, elem.text)
        return ET.tostring(root, encoding="unicode", method="xml")\
                 .replace("<wrap>", "").replace("</wrap>", "").strip()
    except ET.ParseError:
        return xml_str  # return untouched if malformed

def main():
    current_body = ""
    inside_body = False

    for line in sys.stdin:
        if "<soapenv:Body" in line:
            inside_body = True
            current_body = line
        elif "</soapenv:Body>" in line:
            current_body += line
            print(anonymize(current_body))
            inside_body = False
            current_body = ""
        elif inside_body:
            current_body += line
        else:
            print(line, end="")  # pass through non-SOAP-body lines

if __name__ == "__main__":
    main()
