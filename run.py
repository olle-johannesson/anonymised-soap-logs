import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description="Extract (Envelope or Body) and anonymize SOAP content."
    )
    parser.add_argument("--namespace", "-n", help="Optional target namespace (e.g. http://big.arvato-infoscore.de)")
    parser.add_argument("--input", "-i", required=True, help="Path to input logfile")
    parser.add_argument("--output", "-o", help="Optional output file path")
    parser.add_argument(
        "-b", "--body-only",
        action="store_true",
        help="Pass --body-only to extract only the SOAP Body rather than full Envelope"
    )

    args = parser.parse_args()

    extract_cmd = ["python", "extract_soap_bodies.py"]
    if args.body_only:
        extract_cmd.append("--body-only")
    if args.namespace:
        extract_cmd.extend(["--namespace", args.namespace])
    anonymize_cmd = ["python", "anonymize_soap_bodies.py"]

    # Run the pipeline: extract → anonymize
    with open(args.input, "rb") as infile:
        if args.output:
            with open(args.output, "wb") as outfile:
                extract_proc = subprocess.Popen(extract_cmd, stdin=infile, stdout=subprocess.PIPE)
                anonymize_proc = subprocess.Popen(anonymize_cmd, stdin=extract_proc.stdout, stdout=outfile)
                extract_proc.stdout.close()
                anonymize_proc.communicate()
        else:
            extract_proc = subprocess.Popen(extract_cmd, stdin=infile, stdout=subprocess.PIPE)
            anonymize_proc = subprocess.Popen(anonymize_cmd, stdin=extract_proc.stdout)
            extract_proc.stdout.close()
            anonymize_proc.communicate()

if __name__ == "__main__":
    main()
