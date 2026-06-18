# p4-crawler

Web crawler and documentation extractor for intranet and public sites. Crawls static and SPA websites (Angular, React, Storybook), filters content by topic and keywords, downloads pages and attachments (PDF, DOC, XLS), and generates a structured Markdown index.

Supports authenticated sites (Joomla, form-based, HTTP Basic) and handles session re-authentication automatically.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `setup` | `/p4-crawler:setup` | Verifies python3, curl, and pip packages (beautifulsoup4, html2text). Reports status with install instructions. |
| `extract` | `/p4-crawler:extract` | Full pipeline: configure, crawl, deduplicate, filter, download, and generate structured Markdown output. |

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-crawler
```

## Usage

```
/p4-crawler:setup    # check dependencies first
/p4-crawler:extract  # start an extraction session
```

## Output Structure

```
<output_folder>/
├── scrapper-config.json       # session configuration
├── web-map.json               # all crawled nodes (JSONL)
├── web-map-filtered.json      # nodes matching topic/keywords
├── web-map-excluded.json      # excluded nodes
├── INDEX.md                   # final documentation index
└── downloads/
    ├── pages/                 # downloaded pages as Markdown
    └── files/                 # downloaded attachments as Markdown
```

## Dependencies

Python packages required at runtime:

| Package | Install |
|---------|---------|
| `beautifulsoup4` | `pip install beautifulsoup4` |
| `html2text` | `pip install html2text` |
| `playwright` *(optional — SPA mode)* | `pip install playwright && playwright install chromium` |
