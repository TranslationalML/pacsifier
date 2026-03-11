# PACSIFIER

PACSIFIER is an open-source tool written in Python to query, retrieve, and edit data in DICOM format from a radiological PACS server. It can be run directly or via a Docker container.

[![Build](https://img.shields.io/github/actions/workflow/status/TranslationalML/pacsifier/build-test-deploy.yml?branch=master&label=build)](https://github.com/TranslationalML/pacsifier/actions/workflows/build-test-deploy.yml)
[![Docs](https://img.shields.io/github/actions/workflow/status/TranslationalML/pacsifier/docs.yml?branch=master&label=docs)](https://github.com/TranslationalML/pacsifier/actions/workflows/docs.yml)
[![License](https://img.shields.io/github/license/TranslationalML/pacsifier)](https://github.com/TranslationalML/pacsifier/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://translationalml.github.io/pacsifier)

<!-- Uncomment these once you publish a GitHub Release:
[![Latest GitHub Release](https://img.shields.io/github/v/release/TranslationalML/pacsifier)](https://github.com/TranslationalML/pacsifier/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/TranslationalML/pacsifier)](https://github.com/TranslationalML/pacsifier/releases)
-->

> **Full documentation**: [https://translationalml.github.io/pacsifier](https://translationalml.github.io/pacsifier)

> **Windows users:** We strongly recommend using [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) to run PACSIFIER. Linux is the recommended environment.

## Quick Start

### Option 1: Pre-built Docker Image (Recommended)

Pull the latest release from Quay.io — no cloning, no building, no dependency installation required:

```bash
docker pull quay.io/translationalml/pacsifier:latest
```

Run PACSIFIER:

```bash
docker run --rm --net=host \
    -v /path/to/my_dir:/base \
    quay.io/translationalml/pacsifier:latest \
    pacsifier --save --info --queryfile /base/my_query.csv \
    --config /base/my_config.json --out_directory /base/my_output_dir
```

> **Tip:** You can pin to a specific version (e.g. `pacsifier:1.0.0`) instead of `latest`. See [available tags on Quay.io](https://quay.io/repository/translationalml/pacsifier?tab=tags).

Or use the convenience [Docker wrapper scripts](https://translationalml.github.io/pacsifier/docker_wrappers.html):

```bash
pip install pacsifier  # installs the wrapper scripts
docker_pacsifier -c config.json -i -s -q query.csv -d /output
```

### Option 2: Install via pip

```bash
pip install pacsifier
```

> **Note:** When installing via pip, you also need [DCMTK](https://dicom.offis.de/en/dcmtk/dcmtk-tools/) installed on your system (`sudo apt install dcmtk` on Ubuntu).

## Features

- Query PACS metadata and count series/instances per series, written to a TSV file
- Query and retrieve DICOM images from PACS servers
- Move DICOM images between PACS nodes
- Forward DICOM retrieval requests to Karnak (`--karnak`)
- Upload DICOM images to PACS servers
- Anonymize DICOM files (directly or via Karnak gateway)
- Get pseudonyms from the De-ID API
- Create DICOMDIR files
- Extract Carestream reports
- Docker wrapper scripts for simplified usage
- Resume interrupted extractions

## Usage

PACSIFIER provides several CLI commands. How you run them depends on your installation method:

| Install method | How to run commands |
|---|---|
| **Docker** (no install) | `docker run --rm --net=host quay.io/translationalml/pacsifier:latest pacsifier ...` |
| **Docker wrappers** (`pip install pacsifier`) | `docker_pacsifier ...`, `docker_anonymize_dicoms ...` |
| **pip / source** (`pip install pacsifier`) | `pacsifier ...`, `pacsifier-anonymize ...` |

### Available commands

| Command | Docker wrapper | Description |
|---|---|---|
| `pacsifier` | `docker_pacsifier` | Query metadata counts, retrieve, and move DICOM images |
| `pacsifier-pynetdicom-listener` | N/A | Run standalone pynetdicom listener for Karnak forwarding |
| `pacsifier-anonymize` | `docker_anonymize_dicoms` | Anonymize DICOM files |
| `pacsifier-get-pseudonyms` | `docker_get_pseudonyms` | Get pseudonyms from De-ID API or custom mapping |
| `pacsifier-add-karnak-tags` | `docker_add_karnak_tags` | Tag DICOM files for Karnak de-identification |
| `pacsifier-create-dicomdir` | `docker_create_dicomdir` | Create a DICOMDIR file |
| `pacsifier-move-csv` | `docker_move_dumps` | Move info CSV dumps to a separate folder |
| `pacsifier-extract-carestream-report` | `docker_extract_carestream_report` | Extract text from Carestream SR reports |

### Common examples

**With pip/source install** (requires DCMTK on your system):

```bash
# Query metadata counts only (no image download)
pacsifier --count -q query.csv -c config.json -d ./output

# Query and save DICOM images locally
pacsifier --save --info -q query.csv -c config.json -d ./output

# Query and move images to a remote DICOM node
pacsifier --move -q query.csv -c config.json

# Query and forward move requests to Karnak
pacsifier --karnak -q query.csv -c config.json -d ./output

# Export Karnak movescu commands without executing
pacsifier --karnak -q query.csv -c config.json -cf ./karnak_commands.txt

# Override Karnak routing values from CLI
pacsifier --karnak -q query.csv -c config.json \
  --karnak_address 10.1.2.3 --karnak_port 104 --karnak_aet KARNAK \
  --pynetdicom_address 0.0.0.0 --pynetdicom_port 11112 --pynetdicom_aet PACSIFIER

# Upload DICOM images to a PACS server
pacsifier --upload --upload_directory ./dicoms -c config.json

# Resume an interrupted download (skips already downloaded series)
pacsifier --save --resume -q query.csv -c config.json -d ./output

# Anonymize DICOM files
pacsifier-anonymize -d ./data -o ./anonymized --fuzz_acq_dates --remove_private_tags
```

**With Docker** (no DCMTK or Python needed):

```bash
# Using wrapper scripts (pip install pacsifier for the wrappers only)
docker_pacsifier -c config.json -s -i -q query.csv -d ./output
docker_pacsifier -c config.json --count -q query.csv -d ./output
docker_anonymize_dicoms -d ./data -o ./anonymized -a -p

# Or directly with docker run
docker run --rm --net=host \
    -v /path/to/my_dir:/base \
    quay.io/translationalml/pacsifier:latest \
    pacsifier --save --info -q /base/query.csv -c /base/config.json -d /base/output
```

`--count` queries the PACS at series level and writes one row per series to `<output_dir>/count_results.tsv`, printing each series as it is found:

```text
Counting element number 1...
  PatientID=12345 | StudyUID=1.2.3 | SeriesUID=1.2.3.1 | Series=1 T1w [MR] | instances=120
  PatientID=12345 | StudyUID=1.2.3 | SeriesUID=1.2.3.2 | Series=2 T2w [MR] | instances=80
Count results written to: ./output/count_results.tsv
Count summary:
PatientID=12345: series=2, instances=200
```

The TSV file has columns: `PatientID`, `StudyInstanceUID`, `SeriesInstanceUID`, `SeriesDescription`, `SeriesNumber`, `Modality`, `NumberOfSeriesRelatedInstances`.

Results are written **continuously** — if the run is interrupted, restart with `--resume` to skip already-completed query rows:

```bash
pacsifier --count --resume -q query.csv -c config.json -d ./output
```

Run any command with `--help` for the full list of options. See [Docker Wrappers](https://translationalml.github.io/pacsifier/docker_wrappers.html) for more details on the wrapper scripts.

## Configuration

### Config File

PACSIFIER requires a JSON configuration file:

```json
{
    "server_address": "PACS server IP/URL",
    "port": 4242,
    "server_AET": "SERVER_AET",
    "AET": "YOUR_AET",
    "move_AET": "MOVE_DESTINATION_AET",
    "move_port": 11112,
    "batch_size": 30,
    "batch_wait_time": 10,
    "karnak_address": "KARNAK_IP_OR_HOSTNAME",
    "karnak_port": 104,
    "karnak_aet": "KARNAK_AET",
    "pynetdicom_address": "0.0.0.0",
    "pynetdicom_port": 11112,
    "pynetdicom_aet": "PACSIFIER"
}
```

Karnak keys are required when using `--karnak` and optional otherwise.

#### Migrating from PACSMAN

If you are migrating a PACSMAN `config.json`, update the key names and types:
- `server_ip` → `server_address`
- `port`: string → integer
- `move_port`: string → integer
- `batch_size`: string → integer
- `batch_wait_time`: string → integer

### Query File

The query file is a `.csv` file with columns matching DICOM attributes. Supported columns include:
`StudyDate`, `PatientID`, `SeriesDescription`, `Modality`, `ProtocolName`, `StudyInstanceUID`, `SeriesInstanceUID`, `PatientName`, `PatientBirthDate`, `AcquisitionDate`, `DeviceSerialNumber`, `SeriesNumber`, `StudyDescription`, `AccessionNumber`, `SequenceName`, `StudyTime`, `ImageType`.

See the [full documentation](https://translationalml.github.io/pacsifier/usage.html) for query file format, examples, and all CLI options.

## Documentation

Full documentation is available at **[https://translationalml.github.io/pacsifier](https://translationalml.github.io/pacsifier)**, including:

- [Installation Guide](https://translationalml.github.io/pacsifier/installation.html)
- [Command-Line Usage](https://translationalml.github.io/pacsifier/usage.html)
- [Docker Wrappers](https://translationalml.github.io/pacsifier/docker_wrappers.html)
- [Developer Guide](https://translationalml.github.io/pacsifier/developer.html)
- [API Reference](https://translationalml.github.io/pacsifier/api/generated/modules.html)

## Building the Documentation

```bash
make build-docs
```

This generates the HTML documentation in `docs/_build/html`.

## Running Tests

### Via Docker (recommended)

```bash
make build-docker
make test
```

### Locally

#### Install from Source (For Developers)

```bash
git clone https://github.com/TranslationalML/pacsifier.git
cd pacsifier
conda create -n pacsifier_minimal python=3.10
conda activate pacsifier_minimal
pip install -e ".[all]"
```

> **Note:** Source installations require [DCMTK](https://dicom.offis.de/en/dcmtk/dcmtk-tools/) to be installed on your system.

See the [full installation guide](https://translationalml.github.io/pacsifier/installation.html) for all options and details.

#### Run the tests

See the [Developer Guide](https://translationalml.github.io/pacsifier/developer.html) for instructions on running tests locally with a mock DICOM server.

## Contributing

See the [Contributing Guide](https://translationalml.github.io/pacsifier/contributing.html) for guidelines on reporting bugs, requesting features, and submitting pull requests.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

## Citation

If you use PACSIFIER in your work, please cite it. See [How to Cite](https://translationalml.github.io/pacsifier/citing.html).

## Acknowledgments

This project received funding from the Lausanne University Hospital and the Lundin Family Brain Tumour Research Center.

