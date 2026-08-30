# eurostat

**Description:** Eurostat public statistics through the official Statistics REST API in JSON-stat 2.0 format.

## Available APIs

### eurostat_search

**Description:** Search or list a small bundled catalogue of common Eurostat datasets. Query also accepts valid custom Eurostat dataset codes.

**Optional Parameters:**
- `keyword` (): Optional case-insensitive keyword matched against curated dataset codes, names, and descriptions. (default: <nil>)

---

### eurostat_query

**Description:** Query Eurostat dataset observations by keyword or exact dataset code. Returns a CSV file plus a preview.

**Required Parameters:**
- `filepath` (string): Output CSV file path. A .csv extension is appended if missing.

**Optional Parameters:**
- `keyword` (): Dataset code or name keyword. Either 'keyword' or 'dataset' must be provided. (default: <nil>)
- `dataset` (): Exact Eurostat dataset code, for example demo_pjan. Either 'keyword' or 'dataset' must be provided. (default: <nil>)
- `filters` (object): Optional dimension filters used for the query. If omitted, a bounded detail sample is used to add a safe time filter. (default: map[])
- `top` (integer): Maximum decoded observations returned in the CSV file. (default: 50)

---
