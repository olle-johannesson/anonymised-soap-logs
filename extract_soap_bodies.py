#!/usr/bin/env python3
"""
extract_soap_bodies.py

Extract and pretty-print SOAP <Body> blocks from logs.
If a namespace is supplied, only bodies containing that namespace are kept.
If no namespace is supplied, all bodies are extracted.

Reads from stdin, writes to stdout.

Usage:
  # extract only bodies containing the BIG namespace
  cat spring.log \
    | python3 extract_soap_bodies.py -n http://big.arvato-infoscore.de \
    > extracted.xml

  # extract all bodies, regardless of namespace
  cat spring.log \
    | python3 extract_soap_bodies.py \
    > all_bodies.xml
"""
import sys
import re
import argparse
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Patterns
SOAP_NS     = "http://schemas.xmlsoap.org/soap/envelope/"
BODY_TAG    = f"{{{SOAP_NS}}}Body"
ENVELOPE_RE = re.compile(r"<soapenv:Envelope.*?</soapenv:Envelope>", re.DOTALL|re.IGNORECASE)

def pretty_print(xml_str: str) -> str:
    """Indent XML nicely, stripping a temporary wrapper."""
    try:
        doc = minidom.parseString(f"<wrap>{xml_str}</wrap>")
        pretty_xml = doc.toprettyxml(indent="  ")
        lines = []
        for ln in pretty_xml.splitlines():
            s = ln.strip()
            # skip any wrapper tag, opening or closing
            if not s or s.startswith("<wrap") or s.startswith("</wrap"):
                continue
            lines.append(ln)
        return "\n".join(lines)
    except Exception:
        return xml_str.strip()

def extract_inner_body(envelope_xml: str, target_ns: str|None) -> str|None:
    """
    Parse the Envelope block, find <soapenv:Body>, and:
    - if target_ns is None → always return its inner XML
    - else → only if target_ns appears in the block
    Returns pretty-printed inner XML or None.
    """
    try:
        root = ET.fromstring(envelope_xml)
        body = root.find(f".//{BODY_TAG}")
        if body is None:
            return None

        # If a filter namespace was provided, skip blocks that don't contain it
        if target_ns and target_ns not in envelope_xml:
            return None

        # Serialize all children of <Body>
        inner = "".join(ET.tostring(child, encoding="unicode") for child in body)
        return pretty_print(inner)
    except ET.ParseError:
        return None

def main():
    p = argparse.ArgumentParser(
        description="Extract SOAP <Body> blocks, optionally filtering by namespace."
    )
    p.add_argument(
        "-n","--namespace",
        help="Only extract bodies containing this namespace. Omit to extract all."
    )
    args = p.parse_args()

    data = sys.stdin.read()
    if not data.strip():
        sys.exit(0)

    count = 0
    for match in ENVELOPE_RE.finditer(data):
        env = match.group(0)
        body_xml = extract_inner_body(env, args.namespace)
        if body_xml:
            count += 1
            print(f"\n<!-- SOAP BODY #{count} -->")
            print(body_xml)

    if count == 0:
        sys.exit(1)  # no matches (useful in scripts to detect “nothing found”)

if __name__ == "__main__":
    main()