"""Automated router handler for GitHub Issues."""
import os
import sys
import json
import subprocess
from pathlib import Path

def main():
    title = os.environ.get("ISSUE_TITLE", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    author = os.environ.get("ISSUE_AUTHOR", "")

    if not title.lower().startswith("route:"):
        print(f"Issue #{issue_number} does not start with 'route:'. Skipping.")
        return

    query = title[6:].strip()
    if not query or query.startswith("<") and query.endswith(">"):
        query = "Google Maps ranking grids"

    print(f"Routing query: '{query}' for issue #{issue_number} by @{author}")

    # Run cto_legends routing CLI
    cmd = [sys.executable, "-m", "cto_legends", "route", query]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
    except Exception as e:
        print(f"Error running router: {e}")
        data = {"matches": []}

    matches = data.get("matches", [])
    
    if matches:
        top = matches[0]
        mod_id = top.get("id", "cto-legends")
        scope = top.get("scope", "General ecosystem tool.")
        score = top.get("score", 1)
        purpose = top.get("purpose", "")

        comment_body = f"""### cto-legends Automated Routing Receipt

**Requested Task:** `{query}`  
**Dispatched By:** @{author}  

| Recommended Module | Match Score | Primary Purpose |
|---|---|---|
| **[{mod_id}](https://github.com/avalonreset/{mod_id})** | `{score}` | {purpose} |

#### Verified Scope
> {scope}

#### Agent Voice Handoff
Hand this instruction to your autonomous agent:
> *"Use cto-legends to install and run {mod_id} for '{query}'."*

#### Coordinator Execution
```bash
# Install and execute via cto-legends master coordinator
cto-legends install {mod_id} --apply
cto-legends run {mod_id} -- --help
```

*Executed autonomously via cto-legends v0.3.0 router.*
"""
    else:
        comment_body = f"""### cto-legends Routing Receipt

**Requested Task:** `{query}`  
**Dispatched By:** @{author}  

No exact module match was found in the released public module catalog.

#### Current Released Public Modules
- **`legends-geogrid`**: Google Maps local rank grids and visibility studies.
- **`legends-dataforseo-kit`**: SERP queues, keyword research, and offline evidence exporter.
- **`legends-github`**: Repository audits, README improvement, metadata optimization, and releases.
- **`legends-stable-audio-3`**: Continuous audio mixes, instrumental generation, and custom adapters.
- **`legends-obs-kit`**: OBS Studio hardware inspection, settings planning, and verified recording.
- **`legends-obsidian`**: Source-cited vault memory and transactional research evidence.
- **`hyperyap`**: Local voice typing and app dictation.
- **`legends-obs-cursor`**: Animated OBS cursor overlays and click effects.
- **`legends-seo-dungeon`**: 16-bit gamified terminal SEO audit system.

Try rephrasing your task with one of the capabilities above.
"""

    comment_file = Path("comment.md")
    comment_file.write_text(comment_body, encoding="utf-8")
    print("Comment generated successfully.")

if __name__ == "__main__":
    main()
