from __future__ import annotations

import copy
import json

import pytest

from bloom_plant_library import CatalogValidationError, validate_catalog
from bloom_plant_library.catalog import (
    PLANT_FACTS_PATH,
    PLANT_FACTS_SCHEMA_PATH,
    UNRESOLVED_SPECIES_PATH,
    UNRESOLVED_SPECIES_SCHEMA_PATH,
)


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2) + "\n")


def test_checked_in_catalog_validates():
    stats = validate_catalog()

    assert stats.accepted_count == 167
    assert stats.unresolved_count == 3
    assert stats.migration_status_counts == {
        "accepted_auto": 157,
        "accepted_manual": 10,
    }


def test_rejects_accepted_and_unresolved_overlap(tmp_path):
    plant_facts = json.loads(PLANT_FACTS_PATH.read_text())
    unresolved_species = json.loads(UNRESOLVED_SPECIES_PATH.read_text())
    unresolved_species[0]["id"] = plant_facts[0]["id"]

    plant_path = tmp_path / "plant_facts.json"
    unresolved_path = tmp_path / "unresolved_species.json"
    write_json(plant_path, plant_facts)
    write_json(unresolved_path, unresolved_species)

    with pytest.raises(CatalogValidationError, match="overlap"):
        validate_catalog(
            plant_facts_path=plant_path,
            unresolved_species_path=unresolved_path,
            plant_facts_schema_path=PLANT_FACTS_SCHEMA_PATH,
            unresolved_species_schema_path=UNRESOLVED_SPECIES_SCHEMA_PATH,
        )


def test_rejects_manual_record_without_review_reason(tmp_path):
    plant_facts = json.loads(PLANT_FACTS_PATH.read_text())
    unresolved_species = json.loads(UNRESOLVED_SPECIES_PATH.read_text())
    manual_record = next(
        record for record in plant_facts if record["migration_status"] == "accepted_manual"
    )
    modified = copy.deepcopy(plant_facts)
    modified[plant_facts.index(manual_record)]["manual_review_reasons"] = []

    plant_path = tmp_path / "plant_facts.json"
    unresolved_path = tmp_path / "unresolved_species.json"
    write_json(plant_path, modified)
    write_json(unresolved_path, unresolved_species)

    with pytest.raises(CatalogValidationError, match="missing manual review reasons"):
        validate_catalog(
            plant_facts_path=plant_path,
            unresolved_species_path=unresolved_path,
            plant_facts_schema_path=PLANT_FACTS_SCHEMA_PATH,
            unresolved_species_schema_path=UNRESOLVED_SPECIES_SCHEMA_PATH,
        )
