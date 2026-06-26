# Bloom Plant Library

Canonical plant catalog for Bloom apps and controller integrations.

This repository owns plant identity and care-classification data. Runtime
watering behavior, hardware thresholds, replay fixtures, and calibration logic
belong in the controller repository.

## Contents

- `data/plant_facts.json`: accepted plant records.
- `data/unresolved_species.json`: known records that are intentionally blocked
  from catalog promotion until reviewed.
- `schemas/plant_facts.schema.json`: JSON Schema for accepted records.
- `schemas/unresolved_species.schema.json`: JSON Schema for unresolved records.
- `src/bloom_plant_library`: small Python loader and validator.
- `docs/EXPANSION_WORKFLOW.md`: workflow for growing the catalog from app and
  website plant requests.

## Current Catalog

- Accepted records: 167
- Unresolved records: 3
- Auto-supported records: 157
- Manual-review records: 10

The catalog uses controller-family labels because Bloom currently maps each
plant to a care behavior family. Treat those labels as Bloom compatibility data,
not universal botanical facts.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make check
```

Validate the checked-in catalog:

```bash
python -m bloom_plant_library validate
```

Print catalog stats:

```bash
python -m bloom_plant_library stats
```

## Release Contract

Consumers should pin a tag or commit SHA. Catalog changes can affect search,
plant request matching, and controller eligibility decisions.

Recommended versioning:

- Patch: provenance cleanup, typo fixes, alias-only additions.
- Minor: new accepted or unresolved plant records.
- Major: schema changes or semantic changes to controller-family/status fields.
