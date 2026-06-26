# Expansion Workflow

This catalog is expected to grow from the current 167 accepted plants to 500+
plants, then continue growing from mobile and website request demand.

## Record States

Use explicit states so app search can acknowledge demand without implying that
automatic watering is validated for every requested plant.

- `accepted_auto`: reviewed and eligible for Bloom automatic care decisions.
- `accepted_manual`: reviewed, visible to apps, but blocked from automatic
  watering.
- `unresolved`: known candidate that is not ready to promote.
- `requested`: raw user demand before curation.

The current checked-in schemas support `accepted_auto`, `accepted_manual`, and
`unresolved`. Keep raw app and website requests outside `data/plant_facts.json`
until they are curated.

## Request Intake

Recommended request pipeline:

1. Store raw request text, optional image metadata, app surface, locale, and
   timestamp in product storage.
2. Normalize common-name text and compare against accepted records and known
   unresolved records.
3. If matched, increment request demand for the existing plant id.
4. If not matched, create a candidate for review.
5. Curate identity, scientific name, aliases, and care-family assignment.
6. Promote to `accepted_auto`, `accepted_manual`, or `unresolved`.
7. Release a new catalog version and update consumers.

## Expansion Rules

- Prefer scientific-name certainty over common-name convenience.
- Keep aliases/search names separate from canonical identity fields when that
  schema is introduced.
- Do not promote plants to `accepted_auto` unless the care family is compatible
  with Bloom's controller behavior.
- Mark orchids, carnivorous plants, epiphytes, mounted plants, aquatic plants,
  or unusual substrates as manual review unless validated.
- Preserve provenance for every promoted record.

## Suggested Next Schema Additions

Before scaling beyond 500 plants, add:

- `aliases`: app search names and spelling variants.
- `taxonomy`: optional family/genus fields.
- `visibility_status`: app-facing availability separate from controller status.
- `supported_features`: explicit feature flags such as search, care guide, and
  autowater.
- `curation`: review timestamp, reviewer/source, and confidence notes.
