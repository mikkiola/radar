# radar

Automated open-source ecosystem monitoring pipeline powered by Claude API. Collects signals from GitHub, HN, Reddit and AwesomeLists, filters noise, clusters patterns, publishes to Telegram, and renders an interactive knowledge graph.

Live example: [@radar_public](https://t.me/radar_public)  
Interactive graph: [opensource-radar-42558a.gitlab.io](https://opensource-radar-42558a.gitlab.io/)

---

## How it works

```
GitHub / HN / Reddit / AwesomeLists
        ↓
radar_step0.py      → collect projects
        ↓
filter.py           → keyword filter by topic
        ↓
analyze.py          → Claude evaluates each project: SHIFT or NOISE
        ↓
01_Assessments/     → only SHIFT, URL deduplication
        ↓
patterns.py         → Claude clusters assessments into patterns
        ↓
02_Patterns/        → active patterns with observation history
        ↓
telegram_post.py    → post to channel twice a day
        ↓
GitLab Pages        → interactive graph of connections
```

Vault lives in the `vault` branch of the same repository. Obsidian reads it as a local vault. The graph is built from `[[wikilinks]]` in MD files and published automatically on every push.

---

## Emergent properties

The architecture is general enough that you can repurpose it without rewriting.

**Personal research assistant** — swap the filter keywords and prompts, get a radar for any domain: biotech, policy, legal, VC deals.

**Competitive intelligence** — replace GitHub/HN with internal sources (Confluence, Jira, Slack via MCP). Track competitor moves and cluster them into behavioral patterns.

**Self-updating knowledge base** — the vault is a living Obsidian graph. Patterns connect via `[[wikilinks]]`, the graph builds automatically. A human only reviews assessments in the "Human edit" block.

**Falsifiable hypothesis tracker** — `patterns.py` checks each pattern after 6 months: CONFIRMED / REFUTED / TOO_EARLY. Built-in self-correction, not just data accumulation.

**Public site from a private vault** — vault branch → GitLab Pages → public interactive graph. Built with a 60-line custom script, no external graph dependencies.

**AI-powered newsletter template** — `telegram_post.py` generates a post from vault assessments via Claude. Change the data source and prompt — get an automated digest for any topic, any channel.

---

## Scripts

| Script | What it does | Model | Schedule |
|---|---|---|---|
| `radar_step0.py` | Collect: HN + Reddit + GitHub + AwesomeLists | — | Daily |
| `filter.py` | Topic filter | — | Daily |
| `analyze.py` | SHIFT/NOISE evaluation, URL dedup | Sonnet | Daily |
| `update_assessments.py` | Re-evaluate assessments older than 30 days | Sonnet | Daily |
| `patterns.py` | Clustering + archiving + falsification | Sonnet | Every Friday |
| `telegram_post.py` | Generate post and publish | Sonnet | 9:00 and 21:00 |
| `generate_graph.py` | Build graph.json from wikilinks | — | On Pages build |
| `generate_indexes.py` | Generate index.md for vault sections | — | On Pages build |

---

## CI/CD

Repository: `gitlab.com/lyolich777ka/radar`, branches `master` (scripts) and `vault` (data).

| Job | UTC schedule | Local time (UTC+7) |
|---|---|---|
| radar | `0 5 * * *` | 12:00 daily |
| publish | `0 2,14 * * *` | 9:00 and 21:00 |
| patterns | `0 5 * * 5` | 12:00 Friday |
| pages | on push to master | automatic |

---

## Environment variables

All Masked, NOT Protected.

| Variable | What |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GITLAB_PUSH_TOKEN` | Token for pushing to vault branch |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHANNEL_ID` | Channel ID or username |
| `TELEGRAM_OWNER_ID` | Owner Telegram ID (for notifications) |

---

## Vault structure

```
vault branch/
├── 00_Inbox/           new projects for manual review
├── 01_Assessments/     SHIFT assessments (created by analyze.py)
├── 02_Patterns/        active patterns (created by patterns.py)
├── 03_Archive/         dormant and refuted patterns
└── 99_System/          system files, published_posts.log
```
