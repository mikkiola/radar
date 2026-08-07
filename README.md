# radar

A measuring instrument for the agentic/AI market — not a news aggregator, not a GitHub scraper. It's a research platform for accumulating, validating, and evolving structured knowledge about shifts in the AI/MCP/LLM ecosystem: collecting signals from GitHub, HN, Reddit and AwesomeLists, filtering noise, clustering patterns against external analyst opinions, publishing to Telegram, and rendering an interactive knowledge graph.

This is a personal research instrument built for the author's own analysis — not a growth or audience product.

Live example: [@radar_public](https://t.me/radar_public)  
Interactive graph: [opensource-radar-42558a.gitlab.io](https://opensource-radar-42558a.gitlab.io/)

> This GitHub repository is a read-only push mirror of `master`. The
> source of truth is [GitLab](https://gitlab.com/lyolich777ka/radar) —
> please open issues and merge requests there, not here.

---

## How it works

```
GitHub / HN / Reddit / AwesomeLists
        ↓
radar_step0.py      collect projects
        ↓
filter.py           keyword filter by topic
        ↓
analyze.py          Claude: SHIFT or NOISE
        ↓
01_Assessments/     only SHIFT, URL deduplication
        ↓
patterns.py         Claude clusters assessments into patterns
        |
        → fetch_analysts.py   external analysts (Builder Radar, ...)
        |   04_Analysts/      structured claims from external sources
        ↓
02_Patterns/        active patterns with confirmation / divergence notes
        ↓
telegram_post.py    post to channel twice a day
        ↓
GitLab Pages        interactive graph of connections
```

Vault lives in the `vault` branch of the same repository. Obsidian reads it as a local vault. The graph is built from `[[wikilinks]]` in MD files and published automatically on every push.

---

## Five-layer architecture

```
Layer 0 → Sources       GitHub / HN / Reddit / AwesomeLists
Layer 1 → Signals       repositories, articles, posts
Layer 2 → Assessment    SHIFT / NOISE  (analyze.py via Haiku)
Layer 3 → Patterns      signal clusters (patterns.py via Sonnet)
Layer 4 → Meta          our patterns + ExternalAnalyst[] + Forecasts
```

Layer 4 adds external analysts as a separate input to pattern clustering. `patterns.py` receives both our assessments and structured claims from external sources, then looks for:
- where opinions align — signal confirmed
- our unique signal — we see it, analysts do not
- external-only signal — analysts see it, we do not

---

## Emergent properties

**Personal research assistant** — swap filter keywords and prompts, get a radar for any domain: biotech, policy, legal, VC deals.

**Competitive intelligence** — replace GitHub/HN with internal sources (Confluence, Jira, Slack via MCP). Track competitor moves and cluster them into behavioral patterns.

**Self-updating knowledge base** — the vault is a living Obsidian graph. Patterns connect via `[[wikilinks]]`, the graph builds automatically. A human only reviews assessments in the "Human edit" block.

**Falsifiable hypothesis tracker** — `patterns.py` checks each pattern after 6 months: CONFIRMED / REFUTED / TOO_EARLY. Same falsification applies to external analyst claims. Built-in self-correction, not just data accumulation.

**Multi-analyst intelligence layer** — external analysts plug in via config. Builder Radar today, Simon Willison or Latent Space tomorrow. Each analyst carries a trust weight that affects pattern confirmation scoring when multiple analysts are active.

**Public site from a private vault** — vault branch → GitLab Pages → public interactive graph. Built with a 60-line custom script, no external graph dependencies.

**AI-powered newsletter template** — `telegram_post.py` generates a post from vault assessments via Claude. Change the data source and prompt — get an automated digest for any topic, any channel.

---

## Scripts

| Script | What it does | Model | Schedule |
|---|---|---|---|
| `radar_step0.py` | Collect: HN + Reddit + GitHub (new + hot) + AwesomeLists | — | Daily |
| `filter.py` | Topic filter (AI / MCP / LLM / automation) | — | Daily |
| `analyze.py` | SHIFT/NOISE evaluation, URL dedup | Haiku | Daily |
| `update_assessments.py` | Re-evaluate assessments older than 30 days | Haiku | Daily |
| `fetch_analysts.py` | Parse external analysts, extract claims, save to 04_Analysts/ | Haiku | Every Friday |
| `patterns.py` | Clustering + archiving + falsification + external analyst input | Sonnet | Every Friday |
| `telegram_post.py` | Generate post and publish to channel | Sonnet | Twice daily |
| `generate_graph.py` | Build graph.json from wikilinks | — | On Pages build |
| `generate_indexes.py` | Generate index.md for vault sections | — | On Pages build |

---

## CI/CD

Repository: `gitlab.com/lyolich777ka/radar`, branches `master` (scripts) and `vault` (data).

| Job | Cadence | Trigger |
|---|---|---|
| radar | daily | schedule |
| publish | twice daily | `PUBLISH_ONLY=true` |
| analysts | weekly | `PATTERN_MODE=weekly` |
| patterns | weekly | `PATTERN_MODE=weekly` |
| pages | on push to master | `$CI_COMMIT_BRANCH == "master"` |

`analysts` runs before `patterns` in the same weekly pipeline (stage `collect` → stage `patterns`).

---

## Environment variables

All Masked, NOT Protected.

| Variable | What |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GITLAB_PUSH_TOKEN` | Token for pushing to vault branch |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHANNEL_ID` | Channel ID or username (`@radar_public`) |
| `TELEGRAM_OWNER_ID` | Owner Telegram ID for notifications |

---

## Vault structure

```
vault branch/
├── 00_Inbox/           new projects for manual review
├── 01_Assessments/     SHIFT assessments (created by analyze.py)
├── 02_Patterns/        active patterns (created by patterns.py)
├── 03_Archive/         dormant and refuted patterns
├── 04_Analysts/        external analyst claims (created by fetch_analysts.py)
└── 99_System/          system files, published_posts.log
```

---

## External analysts config

```python
EXTERNAL_ANALYSTS = [
    {
        "name": "Builder Radar",
        "url": "https://buttondown.com/Builder-Radar/archive",
        "parser": "parse_buttondown",
        "weight": 0.8,
        "cadence": "weekly"
    },
    # {"name": "Simon Willison", ..., "weight": 1.0},
    # {"name": "Latent Space",   ..., "weight": 0.9},
]
```

Trust weights are inert with a single analyst. They activate when 3+ analysts are present and affect how strongly external confirmation influences pattern scoring.

---

## Requirements / Setup

Python 3. Core scripts depend on `requests`, `anthropic`, and `ghapi` (installed directly in CI; there is no root `requirements.txt`). The docs/Pages build uses `mkdocs` and `mkdocs-material`, listed in [requirements_pages.txt](requirements_pages.txt).

You'll need an Anthropic API key (`ANTHROPIC_API_KEY`) and, for Telegram publishing, a bot token and channel ID — see Environment variables above.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

Olga Stroganova, 2026.

---

## Contributing

This is a personal research tool built for the author's own use. Pull requests are welcome but may not be reviewed quickly, or at all.
