# From a NASA API Call to a Working Feature

**NASA Space Apps Cairo 2026 · Bootcamp workshop: API & Data Integration**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/moghazy17/nsac-2026-api-workshop/blob/main/notebook/NSAC_API_Workshop.ipynb)

Click the badge → **File → Save a copy in Drive** → run cells with **Shift + Enter**.

## Before the workshop (5 min)
1. Get your free NASA API key at <https://api.nasa.gov> (first name, last name, email → Signup).
2. Sign in to [Google Colab](https://colab.research.google.com) with a Google account.
3. Bring a charged laptop. No installs needed.

## What's inside
| Path | What |
|---|---|
| `notebook/NSAC_API_Workshop.ipynb` | The workshop notebook: NeoWs code-along, 3 API cards (EPIC, NeoWs, NASA POWER), USGS join |
| `handouts/NSAC_API_Cards_and_Cheat_Sheet.pdf` | Printable: 3 API cards (EPIC, NeoWs, NASA POWER) + 1-page cheat sheet |
| [`handouts/API_CARDS.md`](handouts/API_CARDS.md) · [`handouts/CHEAT_SHEET.md`](handouts/CHEAT_SHEET.md) | The same, readable on GitHub |
| `data/*_backup.json` | Saved API responses. If the Wi-Fi or an API fails, upload these and the notebook falls back to them |
| `build_notebook.py` | Regenerates the notebook |

## APIs used
- [NASA NeoWs](https://api.nasa.gov): near-Earth asteroids (free key)
- [NASA EPIC](https://epic.gsfc.nasa.gov/about/api): whole-Earth photos from DSCOVR (free key)
- [NASA POWER](https://power.larc.nasa.gov/docs/): daily weather history for any point (no key)
- [USGS Earthquakes](https://earthquake.usgs.gov/fdsnws/event/1/): worldwide earthquakes (no key)

## If you remember only 5 things
1. Test the API URL in your browser first.
2. Get your own free key. A paid key (e.g. an AI key) never goes in a web page or public repo.
3. Save a copy of the data the moment your call works.
4. Take only the fields you need; check units and missing values (-999).
5. Plan for failure: clear message + saved data.
