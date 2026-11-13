# PACSIFIER 1.1.0 release notes (draft)

## Summary

Ships metadata-only workflows documented since 1.0.0 but missing from the Quay `latest` image, restores legacy PACSMAN `--info`-only behaviour, and includes PIER-oriented C-MOVE improvements merged on master.

## Features

- **`--count`**: series-level C-FIND counts written to `<out_directory>/count_results.csv` (`PatientID`, `StudyDate`, `SeriesNumber`, `SeriesDescription`, `NumberOfInstances`); supports `--resume`.
- **`--info` alone**: query PACS and write per-series metadata CSVs without downloading images (patient/study/series folder layout, as in PACSMAN).

## Fixes

- CLI no longer ignores `--info` when `--save` / `--move` are omitted (regression since upload mode was added in 2024).
- Clear error when no action flag is selected.

## Other

- C-MOVE / logging parity improvements for orchestrated deployments (series-level retrieve, PHI-safe logs).

## Upgrade

```bash
docker pull quay.io/translationalml/pacsifier:1.1.0
# or
pip install --upgrade pacsifier==1.1.0
```

Pin by tag or digest on production VMs; avoid relying on `latest` alone.
