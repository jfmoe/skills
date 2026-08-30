# fred

**Description:** Federal Reserve Economic Data series metadata and observations through the official FRED REST JSON API. FRED_API_KEY is read only from server configuration.

## Available APIs

### fred_search

**Description:** Search official FRED series metadata by text. Omit keyword to list the small bundled popular-series catalogue.

**Optional Parameters:**
- `keyword` (): Optional FRED series search text. Empty text is treated as omitted. (default: <nil>)
- `limit` (integer): Maximum series metadata records returned. (default: 20)
- `realtime_start` (): Optional inclusive start of the FRED real-time period for remote search metadata. (default: <nil>)
- `realtime_end` (): Optional inclusive end of the FRED real-time period for remote search metadata. (default: <nil>)

---

### fred_query

**Description:** Query FRED series observations by exact series id or keyword. Returns a CSV file plus a preview. Either 'id' or 'keyword' must be provided.

**Required Parameters:**
- `filepath` (string): Output CSV file path. A .csv extension is appended if missing.

**Optional Parameters:**
- `realtime_end` (): Optional inclusive end of the observation real-time period. Mutually exclusive with vintage_dates. (default: <nil>)
- `vintage_dates` (): Past dates on which data should be viewed. Sent instead of a real-time period, in provider order. (default: <nil>)
- `limit` (integer): Maximum observations returned in the CSV file. (default: 1000)
- `id` (): Exact FRED series identifier, for example GDPC1. Either 'id' or 'keyword' must be provided. (default: <nil>)
- `keyword` (): FRED series search text. Either 'id' or 'keyword' must be provided. (default: <nil>)
- `start` (): Optional first observation date (observation_start upstream). (default: <nil>)
- `frequency` (): Optional lower aggregation frequency using an official FRED frequency code. (default: <nil>) (options: d, w, bw, m, q, sa, a, wef, weth, wew, wetu, wem, wesu, wesa, bwew, bwem)
- `units` (): Optional official FRED value transformation code. (default: <nil>) (options: lin, chg, ch1, pch, pc1, pca, cch, cca, log)
- `aggregation_method` (): Aggregation used with frequency: average, sum, or end of period. Requires frequency. (default: <nil>) (options: avg, sum, eop)
- `output_type` (integer): Official FRED output type: 1 real-time periods; 2 all by vintage; 3 new/revised by vintage; 4 initial releases. (default: 1) (options: )
- `end` (): Optional last observation date (observation_end upstream). (default: <nil>)
- `realtime_start` (): Optional inclusive start of the observation real-time period. Mutually exclusive with vintage_dates. (default: <nil>)

---
