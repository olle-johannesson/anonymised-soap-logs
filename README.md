# SOAP Log Extract & Anonymize Tools

A small toolkit for extracting SOAP `<Body>` fragments from Java Spring log files and anonymizing PII fields using realistic fake data. Everything is packaged in Python scripts and a Docker image for easy cross-platform usage.

## Features

- **Extract**: scans logs for `<soapenv:Envelope>` blocks and pretty-prints the inner `<soapenv:Body>` XML.
    - Optional namespace filter: only output bodies containing the given namespace, or omit the filter to extract all bodies.
- **Anonymize**: replaces PII leaf fields (names, addresses, dates, etc.) with consistent, realistic fake data (German locale) via [Faker](https://faker.readthedocs.io/).
- **Piped or standalone**: two scripts (`extract_soap_bodies.py`, `anonymize_fragments.py`) that you can chain on the command line or run independently.
- **Dockerized**: single `soaptool` image, no local Python or dependencies required.

## Prerequisites

- **Docker** (for containerized usage)
- **OR** Python 3.8+ and `pip` (for local script usage)

## Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/soap-log-tools.git
cd soap-log-tools
```
(Optional) Local Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install faker
```
Build the Docker image
```bash
docker build -t soaptool .
```
Usage

Extract only

Script usage (filter by namespace)
```bash
cat spring.log \
  | python3 extract_soap_bodies.py -n http://big.arvato-infoscore.de \
  > extracted_bodies.xml
```
Script usage (no namespace filter)
```bash
cat spring.log \
  | python3 extract_soap_bodies.py \
  > all_bodies.xml
```
Docker usage (filter by namespace)
```bash
cat spring.log \
  | docker run --rm -i -v "$PWD":/data soaptool extract \
      --namespace http://big.arvato-infoscore.de \
  > extracted_bodies.xml
```
Docker usage (no namespace filter)
```bash
cat spring.log \
  | docker run --rm -i -v "$PWD":/data soaptool extract \
  > all_bodies.xml
```
Anonymize only

Script usage
```bash
cat extracted_bodies.xml \
  | python3 anonymize_fragments.py \
  > anonymized_bodies.xml
```
Docker usage
```bash
cat extracted_bodies.xml \
  | docker run --rm -i -v "$PWD":/data soaptool anonymize \
  > anonymized_bodies.xml
```
Full pipeline

Script pipeline
```bash
cat spring.log \
  | python3 extract_soap_bodies.py -n http://big.arvato-infoscore.de \
  | python3 anonymize_fragments.py \
  > anonymized_bodies.xml
```
Docker pipeline
```bash
cat spring.log \
  | docker run --rm -i -v "$PWD":/data soaptool extract -n http://big.arvato-infoscore.de \
  | docker run --rm -i soaptool anonymize \
  > anonymized_bodies.xml
```
Configuration
	•	Namespace: change the target namespace via -n/--namespace in extract_soap_bodies.py (omit it to extract all bodies).
	•	PII Fields: adjust the TARGET_TAGS set in anonymize_fragments.py to include or exclude tags as needed.

License

This project is licensed under the MIT License. See LICENSE for details.

