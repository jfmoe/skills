# ecb

**Description:** European Central Bank statistics through the official ECB SDMX-JSON data service.

## Available APIs

### ecb_search

**Description:** Search the phase-one curated ECB dataflow allowlist. Omit keyword to list all curated entries; this is not the complete ECB catalogue.

**Optional Parameters:**
- `keyword` (): Optional case-insensitive dataflow id, name, category, or description keyword. Blank text is treated as omitted. (default: <nil>)

---

### ecb_query

**Description:** Query ECB SDMX observations by keyword or exact dataflow/key. Returns a CSV file plus a preview.

**Required Parameters:**
- `filepath` (string): Output CSV file path. A .csv extension is appended if missing.

**Optional Parameters:**
- `start` (): Optional ECB startPeriod in annual, semi-annual, quarterly, monthly, weekly, or daily SDMX format. (default: <nil>)
- `end` (): Optional ECB endPeriod in the same format and frequency as start. (default: <nil>)
- `top` (integer): Maximum observations returned inline. The client requests one extra observation upstream to determine whether results were limited. (default: 50)
- `keyword` (): Optional case-insensitive dataflow id, name, category, or description keyword. Either 'keyword' or 'dataflow' (optionally with 'key') must be provided. (default: <nil>)
- `dataflow` (): ECB dataflow identifier, for example EXR. Either 'keyword' or 'dataflow' must be provided. (default: <nil>)
- `key` (): Optional concrete series key in DSD dimension order. Curated dataflows use their verified sample key when omitted. (default: <nil>)

---
