# API cheat sheet

**Need → find API → read docs → test URL in browser → code the call → inspect JSON → pick fields → clean → save a backup → build the feature → handle errors**

## Status codes
| Code | Meaning |
|---|---|
| **200** | It worked. Still check the list isn't empty `[]` |
| **400** | A parameter is wrong (date format, range too long) |
| **401 / 404** | Wrong address. api.nasa.gov answers 401 for a wrong endpoint |
| **403** | Key wrong or missing (all 40 characters?) |
| **429** | Too many calls. DEMO_KEY = 10/hour per Wi-Fi; your own key = 10,000 |
| **5xx** | Their problem: retry later, use your saved copy |

## Reading JSON
- `{ }` dictionary → look up by **name**: `d["name"]`
- `[ ]` list → look up by **position**: `lst[0]`
- Lost? `print(list(d.keys()))` and `len(lst)`
- Firefox shows JSON as a tree: collapse all, open one box at a time, write the path down.

## Clean before you build
- Text → number: `pd.to_numeric(col)`
- -999 → missing: `col.replace(-999, float("nan"))`
- Dates: `pd.to_datetime(col)`; times are usually UTC
- Units in column names: `tmax_c`, `miss_km`
- GeoJSON order is **[lon, lat]**; USGS time is in **ms**

## The fallback pattern: Python
```python
def fetch_or_backup(url, params, backup_path):
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()                          # 4xx/5xx → error
        data = r.json()
        with open(backup_path, "w") as f:             # save the moment it works
            f.write(json.dumps(data).replace(API_KEY, "***"))   # never save your key
        return data
    except Exception as e:
        print("⚠️ Live data unavailable:", e)          # a clear message
        with open(backup_path) as f:                  # …then the saved copy
            return json.load(f)
```

## The same in JavaScript (fetch)
```js
try {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  localStorage.setItem("backup", JSON.stringify(data));
  show(data);
} catch (e) {
  showMessage("Live data unavailable, showing saved data");
  show(JSON.parse(localStorage.getItem("backup")));
}
```

## Keys
- Get your own at **api.nasa.gov** (1 minute).
- Free NASA key in a web page: OK (worst case: your quota gets used up).
- **Paid key (AI keys!): never** in a web page or public repo.
- Colab: use the 🔑 Secrets panel, not a code cell.

## AI assistants
- Great for explaining docs and drafting parsing code.
- They invent endpoints and field names: check every field exists in the **real** response.
- Never paste a paid key into a prompt or shared code.

**Docs:** [api.nasa.gov](https://api.nasa.gov) · [NASA POWER](https://power.larc.nasa.gov/docs/) · [USGS earthquakes](https://earthquake.usgs.gov/fdsnws/event/1/) · [EPIC](https://epic.gsfc.nasa.gov/about/api) · [JPL SBDB](https://ssd-api.jpl.nasa.gov/doc/sbdb.html)
