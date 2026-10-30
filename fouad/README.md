# NASA Space Apps Cairo 2026 · API & Data Integration · Notebooks

Hands-on notebooks for the workshop *From a NASA API Call to a Working Feature*. They run **online in Google Colab**: nothing to install, no Python setup. A laptop, a browser and a Google account are enough.

## For participants (start here)

1. Click **Open in Colab** next to the notebook you need.
2. Click **File → Save a copy in Drive**. Work in *your* copy, so your edits are kept. (The shared original is read-only.)
3. Get your own free NASA key at <https://api.nasa.gov> (30 seconds) and paste it into `API_KEY` in the first code cell. `DEMO_KEY` works, but runs out quickly in a full room.
4. Run the cells top to bottom (**Shift + Enter**). Cells marked `TODO` are yours to finish. The ✅/❌ cells tell you whether a step works.

| Notebook | Open | Level | What you build |
|---|---|---|---|
| `00` Code-along: NeoWs | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1zFc9H39VD-XWgysfphWUwMe5BtjmZaZT) | Everyone, live with the speaker | The closest asteroids this week, saved backup, one handled error |
| `01` Card: EPIC | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1O7PG6jVeOH8Xw59ms37vIffRyWT6hWN9) | Easy · free key | An Earth card from the latest whole-Earth photo |
| `02` Card: NeoWs list | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Dxie_jV2LZXROGfCdfZb_szI_rNeIzNr) | Medium · free key | An asteroid list with your own twist |
| `03` Card: POWER | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1z5AOb6J0f5RFTYecFfA1qdt8OjfXksOF) | Harder · no key | The chance of a very hot day in Cairo |
| `04` Stretch: join | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1vxwrfaFHt58A3XxExksIXHz_LhF7cRvr) | Fast pairs · no extra key | NeoWs + USGS joined by date |

**Optional add-on: connect an AI (LLM) to your project** (free providers, response types, fallback)

| Notebook | Open | Level | You get |
|---|---|---|---|
| `05` LLM: first call | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EuoJHOCTEBOfUM7X1Jh-Ubt_iqpBiFVP) | Optional · free LLM key | Call a free AI provider with plain `requests` |
| `06` LLM: response types | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1HCg0K56BK5wtWeA-Z9AgMWA6ZNgaO1B_) | Optional · free LLM key | Text, validated JSON, streaming, cut-off answers |
| `07` LLM: fallback chain | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1IIBs6k3b_C-dwZ0j1P8BLyM2TvTE0xUE) | Works with no key | Retry, next provider, cache, honest template |
| `08` LLM: explainer card | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1TPb-WX2-0QW3oayGwICsGjet7MYO6gqh) | Works with no key | NASA data + AI words, checked for invented numbers |

Notebook `08` includes the finished tools from `06` and `07`, so it can be done on its own. Without a key the notebooks still run: they show clearly labelled sample output and the template fallback.

**Keys:** get a free key (Gemini: aistudio.google.com/apikey, Groq: console.groq.com/keys, OpenRouter: openrouter.ai/keys), then in Colab click the 🔑 Secrets icon, add `GEMINI_API_KEY` / `GROQ_API_KEY` / `OPENROUTER_API_KEY`, and switch Notebook access on. Never paste a key into a cell. Free tiers may use your prompts: send no private data. See `LLM_Cheat_Sheet.md`.

All nine are also in one Drive folder: https://drive.google.com/drive/folders/1l2pD9lhRtLkIe8wzzNNlPwotd9zMmt-P

**Good to know**
- Colab already includes `requests`, `pandas`, `numpy` and `matplotlib`. There is nothing to `pip install`.
- Files you save (the `backup/` folder) live only in the current Colab session. They disappear when the session ends. Download them from the file panel on the left if you want to keep them.
- Before you share your own copy, use **Edit → Clear all outputs**. Some outputs contain your key.
- A free NASA key is fine in a notebook. **Never paste a paid key** (for example an AI key) into a notebook you share.
- If Colab says *"Runtime disconnected"*, reconnect and run the cells again from the top.

## For the speaker

| Folder | What |
|---|---|
| `1_participants_starter/` | The starter notebooks (the same ones that are on Drive). |
| `2_speaker_solutions/` | Complete working versions. **Do not share.** Not uploaded to Drive or to this repo. Includes 05–08. |

The Drive notebooks are shared as *anyone with the link can view*. Participants cannot change your originals. To change a notebook, edit it and re-upload it to the same Drive file (*File → Upload notebook* in Colab, or replace the file in Drive), and keep the link.

### Before the session
1. **Run every solution notebook once on the real venue Wi-Fi**, in Colab, with your own key. The notebooks were tested against a local mock that mimics the documented response shapes, **not against the live NASA and USGS servers**. Live APIs change: check field names and limits.
2. **Open each participant link in a private browser window** (no sign-in) to confirm students can open it. They need a Google account to run it.
3. Put the Colab links on the closing slide and in the room chat. The deck's code-along and closing slides now carry the repo link and QR code.
4. A whole room on one Wi-Fi shares one network address, so `DEMO_KEY` can hit its limit fast. Ask everyone to get their own free key before the session.

### Safety nets
- Where a notebook shows *sample* data it is **illustrative or synthetic**, clearly named (`SAMPLE-1 (illustrative)`), with a warning banner. It exists only so a feature can still render when an API is down. It is never real NASA data.
- Saved backups redact the API key (NeoWs copies the key into the links it returns).
- The notebooks include a planned failure (a wrong key) so participants practise the fallback.

### Notes on the techniques
- Energy estimate in notebook `04` is **order of magnitude only**: fixed rocky density (3,000 kg/m³), the *maximum* estimated diameter, no atmosphere effects. The magnitude comparison uses `M = (log10(E) − 4.8) / 1.5`.
- Notebook `03` uses a ±3 day window around a calendar date to get about 140 valid days instead of 20.
- Everything uses 2025-style or fictional scenarios. Nothing in these notebooks builds on the 2026 challenges.
