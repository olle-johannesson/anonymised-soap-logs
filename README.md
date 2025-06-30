# SOAP Log Extract & Anonymize Tools

A small toolkit for extracting SOAP `<Body>` fragments from Java Spring log files and anonymizing PII fields using realistic fake data. Everything is packaged in Python scripts and a Docker image for easy cross-platform usage.

## Features

* **Extract**: Scans logs for `<soapenv:Envelope>` blocks containing a target namespace, then pretty-prints only the inner `<soapenv:Body>` XML.
* **Anonymize**: Replaces PII leaf fields (names, addresses, dates, etc.) with consistent, realistic fake data (German locale) via [Faker](https://faker.readthedocs.io/).
* **Standalone Scripts**: Two Python scripts (`extract_soap_bodies.py`, `anonymize_fragments.py`) can be piped together or run independently.
* **Dockerized**: Single Docker image to avoid local dependencies and environment issues.

## Prerequisites

* Docker (for containerized usage)
* OR Python 3.8+ and pip (for local script usage)

## Installation

### 1. Clone the repo

```bash
git clone https://your.repo.url/soap-log-tools.git
cd soap-log-tools
```

### 2. (Optional) Local Python setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install faker
```

### 3. Build Docker image

```bash
docker build -t soaptool .
```

## Usage

### Extract only

**From stdin to stdout**:

```bash
cat spring.log \
  | python3 extract_soap_bodies.py http://big.arvato-infoscore.de \
  > extracted_bodies.xml
```

**Using Docker**:

```bash
cat spring.log \
  | docker run --rm -i -v "$PWD":/data soaptool extract \
      --namespace http://big.arvato-infoscore.de \
  > extracted_bodies.xml
```

### Anonymize only

```bash
cat extracted_bodies.xml \
  | python3 anonymize_fragments.py \
  > anonymized_bodies.xml
```

**Using Docker**:

```bash
cat extracted_bodies.xml \
  | docker run --rm -i -v "$PWD":/data soaptool anonymize \
  > anonymized_bodies.xml
```

### Full Pipeline

```bash
cat spring.log \
  | python3 extract_soap_bodies.py http://big.arvato-infoscore.de \
  | python3 anonymize_fragments.py \
  > anonymized_bodies.xml
```

Or with Docker:

```bash
docker run --rm -i -v "$PWD":/data soaptool extract \
  --namespace http://big.arvato-infoscore.de < spring.log \
| docker run --rm -i soaptool anonymize > anonymized_bodies.xml
```

## Configuration

* **Namespace**: Change the target namespace via the `--namespace` flag to match different SOAP services.
* **PII Fields**: Adjust `TARGET_TAGS` in `anonymize_fragments.py` to include/exclude tags.

## .dockerignore

Provided to keep your Docker build context clean:

```text
__pycache__/
*.py[cod]
venv/
.env/
build/
dist/
*.egg-info/
.vscode/
.idea/
*.log
*.xml
*.json
```

## License

MIT License. See [LICENSE](LICENSE) for details.
