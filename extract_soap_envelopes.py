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
    args = p.parse_args()

    data = sys.stdin.read()
    if not data.strip():
        sys.exit(0)

    count = 0
    for match in ENVELOPE_RE.finditer(data):
        env = match.group(0)
        envelope_xml = extract_envelope(env, args.namespace)
        if envelope_xml:
            count += 1
            print(f"\n<!-- SOAP ENVELOPE #{count} -->")
            print(envelope_xml)

    if count == 0:
        sys.exit(1)  # no matches (useful in scripts to detect “nothing found”)

if __name__ == "__main__":
    main()