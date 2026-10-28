# API cards

Pick **one** card with your partner. Printable version: [NSAC_API_Cards_and_Cheat_Sheet.pdf](NSAC_API_Cards_and_Cheat_Sheet.pdf).
Each card matches a part of the [notebook](../notebook/NSAC_API_Workshop.ipynb).

---

## A · EPIC: Earth from space on a date
**Easy · needs your free key**

> "A school club wants an 'Earth from space' card for any date someone picks."

**1. Test this URL in your browser first**
```
https://api.nasa.gov/EPIC/api/natural/date/2025-06-01?api_key=YOUR_KEY
```
You get a **list** of the photos taken that day (about 20). Docs: <https://epic.gsfc.nasa.gov/about/api>

**2. Keep only these fields (per photo)**

| Field | Path | Notes |
|---|---|---|
| Image name | `photo["image"]` | Not a link yet (step 3) |
| Time taken | `photo["date"]` | UTC, text → convert to a date |
| Centre latitude | `photo["centroid_coordinates"]["lat"]` | Where the camera points |
| Centre longitude | `photo["centroid_coordinates"]["lon"]` | Cairo ≈ 31.2 |
| Caption | `photo["caption"]` | Optional |

**3. Build the picture link from the date + image name**
```
https://epic.gsfc.nasa.gov/archive/natural/2025/06/01/jpg/epic_1b_20250601094815.jpg
```

**4. The feature:** an "Earth on 1 June 2025" card: the photo centred nearest to Cairo, when it was taken, where it points. Notebook: *Part 2 · Card A*.

> ⚠️ **Trap:** a date with no photos returns **200 OK with an empty list `[]`**. No error, nothing to show. Check `if not photos:` and show a friendly message.

**Done when**
- [ ] Browser URL returns 200 OK
- [ ] Code call returns 200 OK (your key)
- [ ] Clean table: time, lat, lon, image
- [ ] `epic_clean.csv` saved and downloaded
- [ ] Earth card on screen
- [ ] Empty-date case handled with a message

**Stretch:** show all the day's photos in a row (Earth turning in 24 hours) · join NASA POWER temperature for the point the camera faces (date + place).

---

## B · NeoWs: closest asteroids this week
**Medium · needs your free key**

> "A science club wants a weekly post: which asteroids passed closest, how big, how fast?"

**1. Test this URL in your browser first**
```
https://api.nasa.gov/neo/rest/v1/feed?start_date=2025-10-01&end_date=2025-10-07&api_key=YOUR_KEY
```
`near_earth_objects` holds **one list per date**: merge them into one table. Docs: <https://api.nasa.gov> → Asteroids - NeoWs

**2. Keep only these fields (per asteroid `a`)**

| Field | Path | Unit |
|---|---|---|
| Name | `a["name"]` | – |
| Size | `a["estimated_diameter"]["meters"]["estimated_diameter_min" / "_max"]` | m (use the average) |
| Speed | `a["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"]` | km/s, **text** |
| Miss distance | `a["close_approach_data"][0]["miss_distance"]["kilometers"]` | km, **text** |
| Hazardous? | `a["is_potentially_hazardous_asteroid"]` | true / false |

**3. Your twist:** another week (max 7 days!) · only the hazardous ones · the biggest instead of the closest · asteroids per day · distances as "× the distance to the Moon" (`km / 384400`). Notebook: *Part 1* and *Part 2 · Card B*.

> ⚠️ **Traps:** more than 7 days → **400**. Speeds and distances arrive as **text** (`"9" > "10"` is true!) → `pd.to_numeric`. NeoWs copies **your key** into every `links` URL: remove it before you save or share the JSON.

**Done when**
- [ ] Browser URL returns 200 OK
- [ ] Code call returns 200 OK (your key)
- [ ] Clean table, numbers as numbers
- [ ] `neows_clean.csv` saved and downloaded
- [ ] Your list printed on screen
- [ ] Wrong key handled with a clear message

**Stretch:** join USGS earthquakes by date (no key):
```
https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2025-10-01&endtime=2025-10-08&minmagnitude=5
```
Time is in **milliseconds** since 1970 (UTC); coordinates are **[lon, lat, depth]**. Notebook: *Part 3*.

---

## C · NASA POWER: chance of a very hot day
**Harder · no key needed**

> "We're planning an outdoor event in Cairo. How likely is a day above 35 °C on that date?"

**1. Test this URL in your browser first**
```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX&community=RE&latitude=30.0444&longitude=31.2357&start=20050101&end=20241231&format=JSON
```
20 years of daily maximum temperature for Cairo. Dates are `YYYYMMDD`. Docs: <https://power.larc.nasa.gov/docs/>

**2. Keep only these fields**

| Field | Path | Notes |
|---|---|---|
| Daily values | `data["properties"]["parameter"]["T2M_MAX"]` | `{"20050101": 24.9, …}` |
| Units | `data["parameters"]["T2M_MAX"]["units"]` | "C": put it in your column name |
| Missing marker | `data["header"]["fill_value"]` | -999 |

**3. Clean, then compute**
- One row per date; convert `"20050101"` to a real date.
- Replace **-999** with missing and drop those rows (count them first).
- For a calendar day (e.g. 15 June), take every year ± 3 days (≈ 140 days). Chance = share of days above 35 °C.
- Save a CSV whose first lines state the **units** and the **source link**.

Notebook: *Part 2 · Card C*. Our result: 15 June in Cairo → **78%** chance of a day above 35 °C.

> ⚠️ **Trap:** missing days are **-999**, not empty. Average them in and Cairo "gets colder". The most recent days are always -999 (data arrives with a delay).

**Done when**
- [ ] Browser URL returns 200 OK
- [ ] Code call returns 200 OK
- [ ] -999 rows counted and removed
- [ ] Clean table with units in the name
- [ ] `cairo_tmax_daily.csv` saved and downloaded
- [ ] A "% chance" answer on screen

**Stretch:** `parameters=T2M_MAX,PRECTOTCORR,WS10M` (°C, mm/day, m/s) → chance of a wet or windy day · try another city (change `latitude`, `longitude`).
