#!/usr/bin/env python3
"""
extract_soap_bodies.py

Extract and pretty-print SOAP Envelope blocks from logs.
If a namespace is supplied, only envelopes containing that namespace are kept.
If no namespace is supplied, all envelopes are extracted.

Reads from stdin, writes to stdout.

Usage:
  # extract only envelopes containing the BIG namespace
  cat spring.log \
    | python3 extract_soap_bodies.py -n http://big.arvato-infoscore.de \
    > extracted.xml

  # extract all envelopes, regardless of namespace
  cat spring.log \
    | python3 extract_soap_bodies.py \
    > all_envelopes.xml
"""
import sys
import re
import argparse
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Patterns
SOAP_NS     = "http://schemas.xmlsoap.org/soap/envelope/"
ENVELOPE_RE = re.compile(r"<soapenv:Envelope.*?</soapenv:Envelope>", re.DOTALL|re.IGNORECASE)
HEADER_RE = re.compile(r"(<soapenv:Header.*?>)(.*?)(</soapenv:Header>)", re.DOTALL | re.IGNORECASE)

def scrub_header(envelope_xml: str) -> str:
    """Keep Header tags but redact their inner contents."""
    return HEADER_RE.sub(
        lambda m: f"{m.group(1)}\n  <!-- HEADER REDACTED -->\n{m.group(3)}",
        envelope_xml
    )

# Tag expression for SOAP Body
BODY_TAG = f"{{{SOAP_NS}}}Body"

def extract_body(envelope_xml: str, target_ns: str|None) -> str | None:
    """
    Extract only the inner SOAP Body content, optionally filtering by namespace.
    """
    # Skip if namespace filter provided and not present
    if target_ns and target_ns not in envelope_xml:
        return None
    try:
        root = ET.fromstring(envelope_xml)
        body = root.find(f".//{BODY_TAG}")
        if body is None:
            return None
        # Serialize body children
        inner = "".join(ET.tostring(child, encoding="unicode") for child in body)
        return pretty_print(inner)
    except ET.ParseError:
        return None

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

def extract_envelope(envelope_xml: str, target_ns: str|None) -> str | None:
    """
    Return the full SOAP envelope (minus headers),
    optionally filtering by namespace. Returns None if filtered out.
    """
    # Skip if a namespace filter is provided and not present
    if target_ns and target_ns not in envelope_xml:
        return None

    # scrub sensitive header contents, preserve Header tags for mocking
    scrubbed = scrub_header(envelope_xml)

    # Pretty-print the entire envelope for readability
    return pretty_print(scrubbed)

def main():
    p = argparse.ArgumentParser(
        description="Extract SOAP Envelope blocks, optionally filtering by namespace."
    )
    p.add_argument(
        "-n","--namespace",
        help="Only extract envelopes containing this namespace. Omit to extract all."
    )
    p.add_argument(
        "-b", "--body-only",
        action="store_true",
        help="Only extract SOAP Body content (default extracts full Envelope)"
    )
    args = p.parse_args()

    data = sys.stdin.read()
    if not data.strip():
        sys.exit(0)

    count = 0
    for match in ENVELOPE_RE.finditer(data):
        env = match.group(0)
        if args.body_only:
            result = extract_body(env, args.namespace)
            label = "SOAP BODY"
        else:
            result = extract_envelope(env, args.namespace)
            label = "SOAP ENVELOPE"
        if result:
            count += 1
            print(f"\n<!-- {label} #{count} -->")
            print(result)

    if count == 0:
        sys.exit(1)  # no matches (useful in scripts to detect “nothing found”)

if __name__ == "__main__":
    main()