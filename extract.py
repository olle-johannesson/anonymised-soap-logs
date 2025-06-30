#!/usr/bin/env python3
"""
Extract and pretty-print SOAP <Body> content from logs that contain a given XML namespace.
Reads from stdin, writes to stdout.

Usage:
    cat spring.log | python3 extract_soap_bodies.py http://big.arvato-infoscore.de
"""

import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
BODY_TAG = f"{{{SOAP_NS}}}Body"
ENVELOPE_RE = re.compile(r"<soapenv:Envelope.*?</soapenv:Envelope>", re.DOTALL | re.IGNORECASE)

def extract_inner_body(xml_block: str, target_ns: str) -> str:
    """Extract and return pretty-printed inner XML inside <soapenv:Body>."""
    try:
        root = ET.fromstring(xml_block)
        body = root.find(f".//{BODY_TAG}")
        if body is not None and target_ns in xml_block:
            inner = "".join(ET.tostring(e, encoding="unicode") for e in body)
            return pretty_print(inner)
    except ET.ParseError:
        pass
    return None

def pretty_print(xml_str: str) -> str:
    """Indent XML nicely."""
    try:
        parsed = minidom.parseString(f"<wrap>{xml_str}</wrap>")
        pretty = "\n".join(
            line for line in parsed.toprettyxml(indent="  ").splitlines()
            if line.strip() and "<wrap>" not in line and "</wrap>" not in line
        )
        return pretty
    except Exception:
        return xml_str.strip()

def main():
    if len(sys.argv) != 2:
        print("Usage: extract_soap_bodies.py <namespace>", file=sys.stderr)
        sys.exit(1)

    target_ns = sys.argv[1]
    log_data = sys.stdin.read()
    count = 0
    print("Target namespace", target_ns)
    for match in ENVELOPE_RE.finditer(log_data):
        xml_block = match.group(0)
        body = extract_inner_body(xml_block, target_ns)
        if body:
            count += 1
            print(f"\n<!-- SOAP BODY #{count} -->")
            print(body)

    if count == 0:
        print("No matching SOAP bodies found.", file=sys.stderr)

if __name__ == "__main__":
    main()
