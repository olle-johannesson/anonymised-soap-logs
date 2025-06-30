import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Extract and anonymize SOAP body content.")
    parser.add_argument("--namespace", "-n", required=True, help="Target namespace (e.g. http://big.arvato-infoscore.de)")
    parser.add_argument("--input", "-i", required=True, help="Path to input logfile")
    parser.add_argument("--output", "-o", help="Optional output file path")

    args = parser.parse_args()

    extract_cmd = ["python", "extract_soap_bodies.py", args.namespace]
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
