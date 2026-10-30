# Adding an LLM to your project: cheat sheet
NASA Space Apps Cairo 2026 · API & Data Integration

> Free-tier limits and model names change often. Check each provider's dashboard before the event.

## 1. Free providers (all OpenAI-compatible)
| Provider | Base URL | Example model | Secret name | Notes |
|---|---|---|---|---|
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-3.8-flash` | `GEMINI_API_KEY` | Free tier prompts may be used to improve Google products. Limits per project (see AI Studio). |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | Fast. Limits per organisation (about 30 req/min, 1,000/day at last check, unverified). |
| OpenRouter | `https://openrouter.ai/api/v1` | `openrouter/free` or ids ending `:free` | `OPENROUTER_API_KEY` | Free models change. A paid model in your list costs money. |
| Hugging Face | `https://router.huggingface.co/v1` | n/a | `HF_TOKEN` | Free accounts had no credits: not a free option. |

List current models: `GET <base>/models` with the same `Authorization` header.

## 2. The request
```python
r = requests.post(BASE + "/chat/completions",
    headers={"Authorization": "Bearer " + KEY},
    json={"model": MODEL, "max_tokens": 600, "temperature": 0.3,
          "messages": [{"role": "system", "content": "rules"},
                       {"role": "user", "content": "question"}]},
    timeout=30)
text = r.json()["choices"][0]["message"]["content"]
```
Also check `finish_reason` (`stop` = done, `length` = cut off, raise `max_tokens`) and `usage.total_tokens`.

## 3. Response types
| Type | How | Watch out |
|---|---|---|
| Plain text | read `message.content` | can be empty or cut off |
| JSON | ask for JSON in the prompt, add `response_format: {"type":"json_object"}` | only a hint. Strip ``` fences, take first `{` to last `}`, validate keys and allowed values, retry once |
| Streaming | `"stream": true`; lines `data: {...delta.content...}`, ends `data: [DONE]` | some chunks have no `choices` |

## 4. Errors and fallback
| Status | Meaning | Do |
|---|---|---|
| 429 | rate limit | wait (`Retry-After`, max 10 s), retry once, then next provider |
| 500 502 503 504, timeout, network | provider trouble | retry once, then next provider |
| 401 403 | bad key / no access | skip provider |
| 404 | model gone | skip, fix model name |
| 400 | bad request | skip, fix request |
| 200 but empty / wrong shape | unusable | skip |

Chain: **cache → provider 1 → provider 2 → provider 3 → your template**. Say on screen when it is the basic version.

## 5. Safe integration rules
1. Keys in Colab Secrets or environment variables. Never in code, chat or a repo. A paid key never goes in anything you share.
2. Free tiers may train on prompts: no personal or private data.
3. Facts and numbers come from your code; the model only phrases them.
4. Treat the answer as untrusted: parse, validate, check numbers against the facts.
5. Put outside data in a `DATA` block and tell the model to ignore instructions inside it (prompt injection).
6. Label AI text as AI-written, and name the data source. Do not present it as a statement from NASA.
7. Timeouts, short prompts, cache, no calls in tight loops.
