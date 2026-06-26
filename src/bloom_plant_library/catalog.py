from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
SCHEMAS_DIR = REPO_ROOT / "schemas"
PLANT_FACTS_PATH = DATA_DIR / "plant_facts.json"
UNRESOLVED_SPECIES_PATH = DATA_DIR / "unresolved_species.json"
PLANT_FACTS_SCHEMA_PATH = SCHEMAS_DIR / "plant_facts.schema.json"
UNRESOLVED_SPECIES_SCHEMA_PATH = SCHEMAS_DIR / "unresolved_species.schema.json"


class CatalogValidationError(ValueError):
    """Raised when the checked-in plant catalog violates its contract."""


@dataclass(frozen=True)
class CatalogStats:
    accepted_count: int
    unresolved_count: int
    migration_status_counts: dict[str, int]
    controller_family_counts: dict[str, int]
    confidence_counts: dict[str, int]


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def _schema_errors(payload: Any, schema: dict[str, Any]) -> list[str]:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    messages: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages


def _validate_schema(payload: Any, *, schema_path: Path, data_path: Path) -> None:
    errors = _schema_errors(payload, _load_json(schema_path))
    if errors:
        raise CatalogValidationError(
            f"Schema validation failed for {data_path}: {errors[0]}"
        )


def _index_by_id(records: list[dict[str, Any]], *, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record["id"]
        if record_id in indexed:
            raise CatalogValidationError(f"Duplicate {label} id: {record_id}")
        indexed[record_id] = record
    return indexed


def load_catalog(
    *,
    plant_facts_path: str | Path = PLANT_FACTS_PATH,
    unresolved_species_path: str | Path = UNRESOLVED_SPECIES_PATH,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _load_json(plant_facts_path), _load_json(unresolved_species_path)


def validate_catalog(
    *,
    plant_facts_path: str | Path = PLANT_FACTS_PATH,
    unresolved_species_path: str | Path = UNRESOLVED_SPECIES_PATH,
    plant_facts_schema_path: str | Path = PLANT_FACTS_SCHEMA_PATH,
    unresolved_species_schema_path: str | Path = UNRESOLVED_SPECIES_SCHEMA_PATH,
) -> CatalogStats:
    plant_facts_path = Path(plant_facts_path)
    unresolved_species_path = Path(unresolved_species_path)
    plant_facts_schema_path = Path(plant_facts_schema_path)
    unresolved_species_schema_path = Path(unresolved_species_schema_path)

    plant_facts, unresolved_species = load_catalog(
        plant_facts_path=plant_facts_path,
        unresolved_species_path=unresolved_species_path,
    )
    _validate_schema(
        plant_facts,
        schema_path=plant_facts_schema_path,
        data_path=plant_facts_path,
    )
    _validate_schema(
        unresolved_species,
        schema_path=unresolved_species_schema_path,
        data_path=unresolved_species_path,
    )

    accepted_by_id = _index_by_id(plant_facts, label="accepted plant")
    unresolved_by_id = _index_by_id(unresolved_species, label="unresolved species")
    overlapping_ids = sorted(set(accepted_by_id).intersection(unresolved_by_id))
    if overlapping_ids:
        raise CatalogValidationError(
            "Accepted and unresolved records overlap: " + ", ".join(overlapping_ids)
        )

    for plant_id, record in accepted_by_id.items():
        status = record["migration_status"]
        confidence = record["controller_family_confidence"]
        manual_reasons = record["manual_review_reasons"]
        special_handling = record["special_handling"]
        if status == "accepted_auto":
            if manual_reasons:
                raise CatalogValidationError(
                    f"Auto-supported plant {plant_id} has manual review reasons."
                )
            if confidence == "manual_review":
                raise CatalogValidationError(
                    f"Auto-supported plant {plant_id} uses manual_review confidence."
                )
        if status == "accepted_manual":
            if not manual_reasons:
                raise CatalogValidationError(
                    f"Manual-review plant {plant_id} is missing manual review reasons."
                )
            if "manual_review_required" not in special_handling:
                raise CatalogValidationError(
                    f"Manual-review plant {plant_id} is missing manual_review_required."
                )
            if confidence != "manual_review":
                raise CatalogValidationError(
                    f"Manual-review plant {plant_id} must use manual_review confidence."
                )

    return CatalogStats(
        accepted_count=len(plant_facts),
        unresolved_count=len(unresolved_species),
        migration_status_counts=dict(Counter(r["migration_status"] for r in plant_facts)),
        controller_family_counts=dict(Counter(r["controller_family"] for r in plant_facts)),
        confidence_counts=dict(Counter(r["controller_family_confidence"] for r in plant_facts)),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bloom plant catalog tools.")
    parser.add_argument(
        "command",
        choices=("validate", "stats"),
        help="Command to run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    stats = validate_catalog()
    if args.command == "validate":
        print(
            "Catalog valid: "
            f"{stats.accepted_count} accepted, {stats.unresolved_count} unresolved."
        )
        return 0
    print(json.dumps(stats.__dict__, indent=2, sort_keys=True))
    return 0
