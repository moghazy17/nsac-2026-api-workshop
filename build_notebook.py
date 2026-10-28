"""Builds notebook/NSAC_API_Workshop.ipynb. Run: python build_notebook.py"""
import json
from pathlib import Path

cells = []


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src.strip("\n")})


def code(src):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": src.strip("\n")})


# ---------------------------------------------------------------- intro
md("""
# 🚀 From a NASA API Call to a Working Feature
**NASA Space Apps Cairo 2026 · Bootcamp · API & Data Integration workshop**

By the end of this notebook you will have:
1. ✅ one real NASA API call that returns **200 OK**
2. 🧹 the few fields you need in a **clean table** (with units)
3. 💾 a **saved copy** of the data (JSON / CSV)
4. ✨ **one small feature** on screen
5. 🛟 at least **one error handled** with a clear message

**How to use it:** run cells top to bottom with **Shift + Enter**. Work in pairs: one types, one reads the docs.

| Part | What | Time |
|---|---|---|
| 0 | Setup: your key, helpers | 5 min |
| 1 | Code-along: NeoWs, *closest asteroids this week* | 25 min |
| 2 | Your API card (pick one): 🌍 EPIC · ☄️ NeoWs · 🌡️ NASA POWER | 40 min |
| 3 | Stretch: join a second source (USGS earthquakes) | fast pairs |
""")

md("""
## Part 0 · Setup

### Your NASA key, kept out of the code
Never type your key into a code cell: notebooks get shared, screenshotted and pushed to GitHub.

**Option A (best, Colab):** click the 🔑 **Secrets** icon in the left sidebar → *Add new secret* →
name `NASA_API_KEY`, value = your key → switch on **Notebook access**.

**Option B (quick):** just run the next cell; it asks for the key in a hidden box.

No key yet? Get one in 1 minute at <https://api.nasa.gov>. Avoid `DEMO_KEY`: it allows only ~10 calls per hour,
shared by everyone on the same Wi-Fi.
""")

code('''
import os, json, getpass
from datetime import date
import requests
import pandas as pd


def load_key():
    try:  # Option A: Colab Secrets
        from google.colab import userdata
        return userdata.get("NASA_API_KEY")
    except Exception:
        pass
    if os.environ.get("NASA_API_KEY"):  # running on your own machine
        return os.environ["NASA_API_KEY"]
    return getpass.getpass("Paste your NASA API key (hidden): ").strip()  # Option B


API_KEY = load_key()
print(f"Key loaded ✅ ({len(API_KEY)} characters, a NASA key has 40)")
''')

md("""
### Three small helpers we reuse all session
- `get_json()` makes the call and turns error codes into **plain-English messages**.
- `save_json()` saves a backup copy and **removes your key** from it (some APIs echo your key back inside the response!).
- `fetch_or_backup()` is the **fallback pattern**: try the live API; if it fails, use the saved copy.
""")

code('''
class ApiError(Exception):
    pass


HELP = {
    400: "400 Bad Request: a parameter is wrong (date format? range too long?). Re-read the docs.",
    401: "401 Unauthorized: often a wrong address (endpoint) on api.nasa.gov. Compare the URL with the docs.",
    403: "403 Forbidden: your API key is wrong or missing. Check you copied all 40 characters.",
    404: "404 Not Found: the address (endpoint) is wrong. Compare it with the docs.",
    429: "429 Too Many Requests: you hit the rate limit. Wait, or use your own key instead of DEMO_KEY.",
    500: "500 Server Error: the problem is on their side. Retry later, use your saved copy.",
    503: "503 Unavailable: the API is down or overloaded. Use your saved copy.",
}


def hide_key(text):
    return text.replace(API_KEY, "***") if API_KEY else text


def get_json(url, params=None, timeout=30):
    try:
        r = requests.get(url, params=params, timeout=timeout)
    except requests.exceptions.Timeout:
        raise ApiError(f"Timed out after {timeout}s: the API is slow. Try again or use your saved copy.")
    except requests.exceptions.ConnectionError:
        raise ApiError("No connection: check the Wi-Fi, then use your saved copy.")
    if r.status_code != 200:
        raise ApiError(HELP.get(r.status_code, f"HTTP {r.status_code}") + "\\n   API said: " + hide_key(r.text[:200]))
    left = r.headers.get("X-RateLimit-Remaining")
    print("✅ 200 OK" + (f" · calls left this hour: {left}" if left else ""))
    return r.json()


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(hide_key(json.dumps(data, indent=1)))
    print(f"💾 saved {path}")


def fetch_or_backup(url, params, backup_path):
    try:
        data = get_json(url, params)
        save_json(data, backup_path)
        return data
    except ApiError as e:
        print("⚠️ ", e)
        if os.path.exists(backup_path):
            print(f"↩️  Using saved copy: {backup_path}")
            with open(backup_path, encoding="utf-8") as f:
                return json.load(f)
        raise


def download(path):
    """In Colab, files vanish when the session ends, so download them."""
    try:
        from google.colab import files
        files.download(path)
    except ImportError:
        print(f"(not in Colab) file is at {os.path.abspath(path)}")
''')

md("""
### 🛟 No Wi-Fi or API down? Upload the backup files
Your speaker shares ready-made backups (`neows_backup.json`, `epic_backup.json`, `power_backup.json`, `usgs_backup.json`).
Run the cell below **only if you need them**; every card will then fall back to these copies.
""")

code('''
NEED_BACKUPS = False   # ✏️ set to True only if the internet / API fails, then pick the .json files

if NEED_BACKUPS:
    try:
        from google.colab import files
        files.upload()
    except ImportError:
        print("Not in Colab: put the backup files next to this notebook.")
''')

# ---------------------------------------------------------------- part 1
md("""
## Part 1 · Code-along: ☄️ *Closest asteroids this week* (NeoWs)

**The fictional need:** *"A science club wants a weekly post: which asteroids passed closest to Earth, how big, how fast?"*

The workflow we follow, every time:

> **Need → find API → read docs → test URL in browser → code the call → inspect JSON → pick fields → clean → save backup → build feature → handle errors**

### Step 1 · Read the docs
Open <https://api.nasa.gov> → *Browse APIs* → **Asteroids - NeoWs**. The *feed* endpoint:

| Part | Value |
|---|---|
| Endpoint | `https://api.nasa.gov/neo/rest/v1/feed` |
| Parameters | `start_date`, `end_date` (`YYYY-MM-DD`, **max 7 days apart**) |
| Key | `api_key` |
""")

md("""
### Step 2 · Test the URL in your browser first
If it doesn't work in the browser, it won't work in your code. Copy the URL printed below, replace `YOUR_KEY`
with your key, and open it (Firefox shows JSON nicely; in Chrome tick *Pretty-print*).
""")

code('''
NEO_URL = "https://api.nasa.gov/neo/rest/v1/feed"
START, END = "2025-10-01", "2025-10-07"   # fixed dates = same result every time

print(f"{NEO_URL}?start_date={START}&end_date={END}&api_key=YOUR_KEY")
''')

md("""
### Step 3 · Code the call
`requests` builds the same URL from a dictionary of parameters. We use `fetch_or_backup`, so a backup copy is saved
**the moment the call works**.
""")

code('''
params = {"start_date": START, "end_date": END, "api_key": API_KEY}
feed = fetch_or_backup(NEO_URL, params, "neows_backup.json")
''')

md("""
### Step 4 · Inspect the JSON: boxes inside boxes 📦
JSON is just **dictionaries** `{}` (look up by name) and **lists** `[]` (look up by position), nested inside each other.
""")

code('''
print("Top-level keys:", list(feed.keys()))
print("How many asteroids:", feed["element_count"])
print("Dates inside 'near_earth_objects':", sorted(feed["near_earth_objects"]))
''')

code('''
first_day = sorted(feed["near_earth_objects"])[0]
first = feed["near_earth_objects"][first_day][0]
print(hide_key(json.dumps(first, indent=2)))   # 👀 look at "links": the API echoes your key back!
''')

md("""
**Find the path to each field we need:**

| We want | Path in the JSON | Unit |
|---|---|---|
| name | `["name"]` | – |
| size | `["estimated_diameter"]["meters"]["estimated_diameter_min" / "_max"]` | m |
| speed | `["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"]` | km/s (**text!**) |
| miss distance | `["close_approach_data"][0]["miss_distance"]["kilometers"]` | km (**text!**) |
| hazardous? | `["is_potentially_hazardous_asteroid"]` | true/false |
""")

md("### Step 5 · Pick only the fields you need → a flat table")

code('''
rows = []
for day, asteroids in feed["near_earth_objects"].items():
    for a in asteroids:
        if not a["close_approach_data"]:      # empty list → skip, don't crash
            continue
        approach = a["close_approach_data"][0]
        size = a["estimated_diameter"]["meters"]
        rows.append({
            "name": a["name"],
            "date": day,
            "diameter_m": (size["estimated_diameter_min"] + size["estimated_diameter_max"]) / 2,
            "speed_km_s": approach["relative_velocity"]["kilometers_per_second"],
            "miss_distance_km": approach["miss_distance"]["kilometers"],
            "hazardous": a["is_potentially_hazardous_asteroid"],
        })

neo = pd.DataFrame(rows)
print(neo.dtypes)   # 🚩 speed and distance are 'object' = text, not numbers
neo.head()
''')

md("""
### Step 6 · Clean: types, units, dates
Text that looks like a number is still text: `"9" > "10"` is `True`. Convert first, then sort.
We also turn kilometres into something humans feel: **distance to the Moon** (384,400 km).
""")

code('''
neo["speed_km_s"] = pd.to_numeric(neo["speed_km_s"], errors="coerce")
neo["miss_distance_km"] = pd.to_numeric(neo["miss_distance_km"], errors="coerce")
neo["date"] = pd.to_datetime(neo["date"])
neo["miss_distance_moons"] = neo["miss_distance_km"] / 384_400

neo = neo.sort_values("miss_distance_km").reset_index(drop=True)
neo.head(10)
''')

md("### Step 7 · Save the clean table (CSV) and download it")

code('''
neo.to_csv("neows_clean.csv", index=False)
download("neows_clean.csv")
download("neows_backup.json")
''')

md("### Step 8 · The feature ✨ *Closest asteroids this week*")

code('''
print(f"☄️  Closest asteroids to Earth, {START} → {END}\\n")
for i, r in neo.head(5).iterrows():
    flag = "  ⚠️ potentially hazardous" if r["hazardous"] else ""
    print(f"{i + 1}. {r['name']:<20} {r['miss_distance_moons']:5.1f} × Moon distance · "
          f"~{r['diameter_m']:4.0f} m wide · {r['speed_km_s']:4.1f} km/s{flag}")
print(f"\\n{neo['hazardous'].sum()} of {len(neo)} asteroids this week are flagged hazardous.")
print("Source: NASA NeoWs, api.nasa.gov")
''')

md("""
### Step 9 · Planned failure 💥 and the fallback 🛟
Live demos break: wrong key, rate limits, slow Wi-Fi. Let's break it on purpose.
""")

code('''
# 1) A wrong key → clear message instead of a scary traceback
try:
    get_json(NEO_URL, {**params, "api_key": "WRONG_KEY_123"})
except ApiError as e:
    print("⚠️ ", e)
''')

code('''
# 2) Asking for too many days (docs say max 7) → 400
try:
    get_json(NEO_URL, {**params, "end_date": "2025-10-20"})
except ApiError as e:
    print("⚠️ ", e)
''')

code('''
# 3) The fallback: the same call with a broken key still shows data, from the saved copy
feed_again = fetch_or_backup(NEO_URL, {**params, "api_key": "WRONG_KEY_123"}, "neows_backup.json")
print("Asteroids available:", feed_again["element_count"])
''')

md("""
**🧠 The pattern you'll reuse in the hackathon:**
`call → check status → pick fields → clean → save → show → (if it fails: clear message + saved copy)`
""")

# ---------------------------------------------------------------- part 2
md("""
## Part 2 · Your API card (pick ONE with your partner)

| Card | Level | Key? | Feature |
|---|---|---|---|
| 🌍 **A · EPIC** | easy | yes | *Earth from space* on a chosen date |
| ☄️ **B · NeoWs** | medium | yes | your own twist on the asteroid list |
| 🌡️ **C · NASA POWER** | harder | no | *chance of a very hot day* in Cairo on a date |

**Checkpoints:** 🕐 min 70: 200 OK · 🕑 min 85: clean table · 🕒 min 100: feature + saved file
""")

# --- card A
md("""
---
### 🌍 Card A · EPIC: *Earth from space on a chosen date*
EPIC is a camera on the DSCOVR satellite, 1.5 million km away. It photographs the whole sunlit Earth several times a day.

- Docs: <https://epic.gsfc.nasa.gov/about/api>
- Endpoint: `https://api.nasa.gov/EPIC/api/natural/date/YYYY-MM-DD?api_key=YOUR_KEY`
- Fields to keep: `image`, `date`, `caption`, `centroid_coordinates` (lat/lon the camera is looking at)
- ⚠️ Trap: a date with no photos returns **200 OK with an empty list `[]`**. No error, just nothing.
""")

code('''
EPIC_DATE = "2025-06-01"   # ✏️ try your birthday (photos exist from mid-2015 on)

photos = fetch_or_backup(f"https://api.nasa.gov/EPIC/api/natural/date/{EPIC_DATE}",
                         {"api_key": API_KEY}, "epic_backup.json")
if not photos:
    print(f"📭 No EPIC photos for {EPIC_DATE}. Try another date.")
else:
    print(f"{len(photos)} photos on {EPIC_DATE}")
''')

code('''
epic = pd.DataFrame([{
    "image": p["image"],
    "time_utc": pd.to_datetime(p["date"]),
    "center_lat": p["centroid_coordinates"]["lat"],
    "center_lon": p["centroid_coordinates"]["lon"],
} for p in photos])
epic.head()
''')

md("""
The JSON only gives the **image name**. The docs explain how to build the picture's address from the date + name:
`https://epic.gsfc.nasa.gov/archive/natural/YYYY/MM/DD/jpg/<image>.jpg`
""")

code('''
from IPython.display import HTML, display


def epic_image_url(image_name, day):
    y, m, d = day.split("-")
    return f"https://epic.gsfc.nasa.gov/archive/natural/{y}/{m}/{d}/jpg/{image_name}.jpg"


# The feature: an "Earth from space" card, picking the photo centered nearest to Cairo
CAIRO_LON = 31.2
best = epic.loc[(epic["center_lon"] - CAIRO_LON).abs().idxmin()]
display(HTML(f"""
<div style="font-family:sans-serif;max-width:420px;border:1px solid #ccc;border-radius:12px;padding:12px">
  <img src="{epic_image_url(best['image'], EPIC_DATE)}" style="width:100%;border-radius:8px">
  <h3 style="margin:8px 0 4px">🌍 Earth on {EPIC_DATE}</h3>
  <div>Taken {best['time_utc']:%H:%M} UTC from 1.5 million km away,
  centred over lat {best['center_lat']:.1f}°, lon {best['center_lon']:.1f}°.</div>
  <small>Source: NASA EPIC / DSCOVR</small>
</div>"""))
''')

code('''
epic.to_csv("epic_clean.csv", index=False)
download("epic_clean.csv")
''')

md("""
✅ **Done when:** 200 OK · table with time + centre point · saved CSV · Earth card on screen · the empty-date case handled.
⭐ **Stretch:** show all photos of the day in a row; or join with Card C weather for the same date.
""")

# --- card B
md("""
---
### ☄️ Card B · NeoWs: *your own twist*
You already have the pipeline from Part 1. Make it yours (pick one or more):
1. Change `START`/`END` to another week (max 7 days!) and re-run Part 1.
2. Show **only hazardous** asteroids.
3. Show the **biggest** asteroids instead of the closest.
4. Count asteroids **per day** of the week.
""")

code('''
# 2) only hazardous, closest first
neo[neo["hazardous"]].head(5)
''')

code('''
# 3) the biggest ones
neo.sort_values("diameter_m", ascending=False).head(5)[["name", "date", "diameter_m", "miss_distance_moons"]]
''')

code('''
# 4) asteroids per day
per_day = neo.groupby("date").size()
per_day.index = per_day.index.strftime("%a %d %b")
per_day
''')

md("""
✅ **Done when:** a new 200 OK call (new dates) · clean table · saved CSV · your feature printed.
⭐ **Stretch:** Part 3 joins the asteroids with real earthquakes.
""")

# --- card C
md("""
---
### 🌡️ Card C · NASA POWER: *chance of a very hot day*
**The fictional need:** *"We're planning an outdoor event in Cairo. How likely is a day above 35 °C on that date?"*

- Docs: <https://power.larc.nasa.gov/docs/services/api/temporal/daily/>
- Endpoint: `https://power.larc.nasa.gov/api/temporal/daily/point`, **no key needed**
- Parameters: `parameters=T2M_MAX` (max temperature at 2 m), `latitude`, `longitude`, `start`, `end` (`YYYYMMDD`), `community=RE`, `format=JSON`
- ⚠️ Trap: missing days are **-999**, not empty. Average them in and Cairo gets a lot colder 🙃
""")

code('''
LAT, LON = 30.0444, 31.2357           # Cairo
POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
power_params = {
    "parameters": "T2M_MAX", "community": "RE", "format": "JSON",
    "latitude": LAT, "longitude": LON,
    "start": "20050101", "end": date.today().strftime("%Y%m%d"),   # ~20 years up to today
}
power = fetch_or_backup(POWER_URL, power_params, "power_backup.json")
print("Units:", power["parameters"]["T2M_MAX"])
''')

code('''
values = power["properties"]["parameter"]["T2M_MAX"]          # {"20050101": 24.9, ...}
weather = pd.DataFrame({"tmax_c": pd.Series(values)})
weather.index = pd.to_datetime(weather.index, format="%Y%m%d")

print("Days:", len(weather), "| days marked -999:", (weather["tmax_c"] == -999).sum())
weather.tail(8)   # the most recent days are not processed yet → -999
''')

code('''
weather["tmax_c"] = weather["tmax_c"].replace(-999, float("nan"))
weather = weather.dropna()
print("Clean days:", len(weather), "| coldest:", weather["tmax_c"].min(), "°C | hottest:", weather["tmax_c"].max(), "°C")
''')

md("""
**The feature.** For a calendar day, look at every year in the data, a few days either side
(±3 days → ~140 samples instead of ~20), and count how often it went above the threshold.
""")

code('''
def chance_of_hot_day(df, month, day, threshold=35, window=3):
    days = []
    for year in df.index.year.unique():
        try:
            center = pd.Timestamp(year, month, day)
        except ValueError:            # 29 Feb in a normal year
            continue
        days += list(pd.date_range(center - pd.Timedelta(days=window), center + pd.Timedelta(days=window)))
    sample = df.loc[df.index.intersection(days), "tmax_c"]
    return 100 * (sample > threshold).mean(), len(sample)


MONTH, DAY, THRESHOLD = 6, 15, 35     # ✏️ change me
pct, n = chance_of_hot_day(weather, MONTH, DAY, THRESHOLD)
print(f"🌡️ Cairo, {pd.Timestamp(2000, MONTH, DAY):%d %B}: {pct:.0f}% chance of a day above {THRESHOLD} °C")
print(f"   based on {n} days of NASA POWER data, {weather.index.year.min()}–{weather.index.year.max()}")
''')

code('''
# A tiny "climate calendar": the 15th of every month
pd.DataFrame(
    [(pd.Timestamp(2000, m, 15).strftime("%B"), round(chance_of_hot_day(weather, m, 15, THRESHOLD)[0]))
     for m in range(1, 13)],
    columns=["month", f"% days > {THRESHOLD} °C"],
)
''')

md("A CSV that someone else can trust carries its **units** and its **source**:")

code('''
with open("cairo_tmax_daily.csv", "w", encoding="utf-8") as f:
    f.write(f"# Daily max temperature at 2 m (T2M_MAX), units: degrees C, location: Cairo {LAT},{LON}\\n")
    f.write("# Source: NASA POWER daily API, https://power.larc.nasa.gov ; -999 (missing) rows removed\\n")
    weather.to_csv(f, index_label="date")
download("cairo_tmax_daily.csv")
''')

md("""
✅ **Done when:** 200 OK · -999 removed · clean table with units · saved CSV · a "% chance" answer on screen.
⭐ **Stretch:** add rain (`PRECTOTCORR`, mm/day) and wind (`WS10M`, m/s) to `parameters` (comma-separated) and compute *chance of a wet day*.
""")

# ---------------------------------------------------------------- part 3
md("""
## Part 3 · Stretch: join a second source 🔗 (USGS earthquakes)
**Integration = joining two sources on a shared field** (date, place or ID).

USGS publishes every earthquake worldwide, **no key needed**. Docs: <https://earthquake.usgs.gov/fdsnws/event/1/>

Our shared field: **the date**. Same week as the asteroids (needs Part 1 run first).
""")

code('''
quake_json = fetch_or_backup(
    "https://earthquake.usgs.gov/fdsnws/event/1/query",
    {"format": "geojson", "starttime": START, "endtime": "2025-10-08", "minmagnitude": 5},
    "usgs_backup.json",
)
quakes = pd.DataFrame([{
    "time": pd.to_datetime(f["properties"]["time"], unit="ms"),   # ⚠️ milliseconds since 1970, UTC
    "magnitude": f["properties"]["mag"],
    "place": f["properties"]["place"],
    "lon": f["geometry"]["coordinates"][0],                        # ⚠️ GeoJSON order is [lon, lat, depth]
    "lat": f["geometry"]["coordinates"][1],
} for f in quake_json["features"]])
quakes["date"] = quakes["time"].dt.normalize()
quakes.sort_values("magnitude", ascending=False).head()
''')

code('''
# One row per day from each source, then join on the shared field "date"
asteroids_per_day = neo.groupby("date").agg(asteroids=("name", "size"),
                                            closest_moons=("miss_distance_moons", "min"))
quakes_per_day = quakes.groupby("date").agg(quakes_m5=("magnitude", "size"),
                                            strongest=("magnitude", "max"))
week = asteroids_per_day.join(quakes_per_day, how="left").fillna({"quakes_m5": 0})
week
''')

md("""
### Make the energy feel real
How much energy would an asteroid carry *if* it hit? (It didn't: these all missed! This is a rough illustration.)

- mass = density × volume, assuming a rocky asteroid (~3,000 kg/m³) and a sphere
- kinetic energy **E = ½ m v²** (joules)
- earthquake energy ↔ magnitude: **log₁₀ E ≈ 1.5 M + 4.8** (Gutenberg–Richter)
""")

code('''
import math

DENSITY = 3000            # kg/m³, an assumption: say so in your app!
MEGATON_TNT = 4.184e15    # joules

neo["energy_j"] = 0.5 * DENSITY * (math.pi / 6) * neo["diameter_m"] ** 3 * (neo["speed_km_s"] * 1000) ** 2
neo["megatons_tnt"] = neo["energy_j"] / MEGATON_TNT
neo["quake_magnitude_equiv"] = (neo["energy_j"].apply(math.log10) - 4.8) / 1.5

strongest = quakes.loc[quakes["magnitude"].idxmax()]
big = neo.sort_values("energy_j", ascending=False).iloc[0]
print(f"Biggest punch this week: {big['name']} (~{big['diameter_m']:.0f} m, {big['speed_km_s']:.1f} km/s)")
print(f"  ≈ {big['megatons_tnt']:,.0f} megatons of TNT ≈ the energy of a magnitude {big['quake_magnitude_equiv']:.1f} earthquake")
print(f"Strongest real earthquake that week: M{strongest['magnitude']} {strongest['place']}")
''')

# ---------------------------------------------------------------- wrap-up
md("""
## 🤖 Using AI assistants (ChatGPT / Claude / Gemini / Copilot)
Great for *"explain these docs"* and *"draft code to parse this JSON"*. But AI **often invents endpoints and field names**.
Rule: **check every field against the real response** before you build on it.
""")

code('''
def check_fields(obj, fields):
    for f in fields:
        print(("✅ " if f in obj else "❌ NOT in the response: ") + f)


# Fields an AI suggested for a NeoWs asteroid. Two of them don't exist:
check_fields(first, ["name", "is_potentially_hazardous_asteroid", "diameter_km", "estimated_diameter", "danger_level"])
''')

md("""
## 📌 If you remember only 5 things
1. **Test the API URL in your browser first.** If it fails there, it fails in code.
2. **Get your own free key.** `DEMO_KEY` runs out fast. A free NASA key in a web page is OK; a **paid key (e.g. an AI key) never goes in a web page or a public repo**.
3. **Save a copy the moment your call works.** Build on the copy, then go live.
4. **Take only the fields you need.** Check units, text-vs-number, and missing values (-999) first.
5. **Plan for failure:** slow or down API → clear message + your saved data.

## ⏱️ Your 48-hour hackathon data plan
- **Hours 0–3:** one real call working + response saved. Nothing else matters yet.
- **Then:** build your feature on the saved copy (fast, no rate limits, works offline).
- **Later:** switch to live data, add a second source if time allows.
- **Don't waste time on:** your own backend/database, many APIs at once, huge downloads, a "perfect" pipeline.

**Links:** [api.nasa.gov](https://api.nasa.gov) · [NASA POWER docs](https://power.larc.nasa.gov/docs/) ·
[USGS earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/) · [EPIC API](https://epic.gsfc.nasa.gov/about/api) ·
[JPL Small-Body Database API](https://ssd-api.jpl.nasa.gov/doc/sbdb.html)
""")

nb = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"cell-{i:02d}"
out = Path(__file__).parent / "notebook" / "NSAC_API_Workshop.ipynb"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("wrote", out, len(cells), "cells")
