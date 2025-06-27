#!/usr/bin/env python3
"""
Extract SOAP <Body> contents from Spring logs, filtering by target XML namespace.

Usage:
    cat spring.log | python3 extract_soap_bodies.py \
        --namespace http://big.arvato-infoscore.de

Options:
    -n, --namespace        Required. The XML namespace to match (e.g., for filtering SOAP messages).
    -s, --soap-namespace   Optional. Default is SOAP 1.1 namespace:
                           http://schemas.xmlsoap.org/soap/envelope/
"""

import sys
import re
import argparse
import xml.etree.ElementTree as ET

DEFAULT_SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
SOAP_ENV_RE = re.compile(
    r"<soapenv:Envelope.*?</soapenv:Envelope>",
    re.DOTALL | re.IGNORECASE
)

def extract_inner_body(xml_block: str, target_ns: str, soap_ns: str) -> str | None:
    """Parse a SOAP envelope block and return the contents of <soapenv:Body> if it matches the target NS."""
    try:
        root = ET.fromstring(xml_block)
        body = root.find(f".//{{{soap_ns}}}Body")
        if body is not None and target_ns in xml_block:
            return "".join(ET.tostring(e, encoding="unicode") for e in body).strip()
    except ET.ParseError:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Extract SOAP Body blocks by namespace.")
    parser.add_argument(
        "-n", "--namespace", required=True,
        help="Target XML namespace to filter for (e.g. http://big.arvato-infoscore.de)"
    )
    parser.add_argument(
        "-s", "--soap-namespace", default=DEFAULT_SOAP_NS,
        help=f"SOAP Envelope namespace (default: {DEFAULT_SOAP_NS})"
    )
    args = parser.parse_args()

    log_data = sys.stdin.read()
    match_count = 0

    for match in SOAP_ENV_RE.finditer(log_data):
        envelope = match.group(0)
        inner_body = extract_inner_body(envelope, args.namespace, args.soap_namespace)
        if inner_body:
            match_count += 1
            print(f"\n--- SOAP BODY #{match_count} ---")
            print(inner_body)

    if match_count == 0:
        print("No matching SOAP body found for given namespace.", file=sys.stderr)

if __name__ == "__main__":
    main()
