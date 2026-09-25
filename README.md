<div align="center">
  <a href="https://cto-legends.com">
    <img src="assets/banner.svg" alt="cto-legends: agent skills and tool management for the open-source legends ecosystem" width="100%" />
  </a>
</div>

<p>
  <a href="https://www.skool.com/ai-marketing-hub-pro"><img align="left" src="https://img.shields.io/badge/community-ai--marketing--hub--pro-ff0000?style=flat-square&labelColor=000000" alt="community: ai-marketing-hub-pro" /></a>
  <a href="https://github.com/avalonreset/cto-legends/blob/main/LICENSE"><img align="right" src="https://img.shields.io/badge/license-MIT-ff0000?style=flat-square&labelColor=000000" alt="License MIT" /></a>
</p>
<br clear="both" />

Modular AI agent skills, deterministic tool runtimes, and local intelligence systems.

The ecosystem combines independent modules with one central entry point, `cto-legends`. This is the single-skill router: install one skill; every module loads on demand. Agents load the relevant Markdown instructions on demand and use executable tools where needed. Setup and execution support depend on the module and agent application:

<p>
  <img src="https://img.shields.io/badge/claude-000000?style=flat-square" alt="claude" />
  <img src="https://img.shields.io/badge/codex-000000?style=flat-square" alt="codex" />
  <img src="https://img.shields.io/badge/gemini-000000?style=flat-square" alt="gemini" />
  <img src="https://img.shields.io/badge/grok-000000?style=flat-square" alt="grok" />
  <img src="https://img.shields.io/badge/cursor-000000?style=flat-square" alt="cursor" />
  <img src="https://img.shields.io/badge/windsurf-000000?style=flat-square" alt="windsurf" />
  <img src="https://img.shields.io/badge/aider-000000?style=flat-square" alt="aider" />
  <img src="https://img.shields.io/badge/muse-000000?style=flat-square" alt="muse" />
</p>

---

### Start with `cto-legends`

Give your agent the [cto-legends repository](https://github.com/avalonreset/cto-legends) and describe what you want to do. The central skill helps discover modules, load their instructions, and check their prerequisites.

- **One entry point:** the single-skill router; a capability index points to independent Markdown workflows.
- **Install what you need:** executable modules use their documented runtimes; some workflows need only instructions and available tools.
- **Check readiness:** installation, credentials, browser support, and task inputs are distinct checks.
- **Keep modules independent:** each product retains its own release and scope. Agent discovery and execution still depend on the host setup.

### The ecosystem

<table width="100%"><tr>
<td width="20%" valign="top"><a href="https://github.com/avalonreset/cto-legends"><strong><code>cto-legends</code></strong></a><br/><img src="assets/column-width-240.svg" width="240" height="1" alt="" /></td>
<td width="20%" valign="top"><strong>single-skill-router</strong><br/><img src="assets/column-width-240.svg" width="240" height="1" alt="" /></td>
<td width="60%" valign="top">central capability index, module manager, and execution router for legends.<br/><img src="assets/column-width-720.svg" width="720" height="1" alt="" /></td>
</tr></table>

<div><img src="assets/ecosystem-separator.svg" width="100%" height="40" alt="" /></div>

<table width="100%">
<tr><th width="20%" align="left"><img src="assets/heading-module.svg" width="100%" alt="Module" /></th><th width="20%" align="left"><img src="assets/heading-focus.svg" width="100%" alt="Focus" /></th><th width="60%" align="left"><img src="assets/heading-capabilities.svg" width="100%" alt="What you can do" /></th></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-empire"><strong>legends-empire</strong></a></td><td valign="top">Business &amp; Research Memory</td><td valign="top">Preserve source-cited research and update vault notes through recoverable transactions. Unified Empire workspace onboarding is in development.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-grant"><strong>legends-grant</strong></a></td><td valign="top">Grant Research</td><td valign="top">Business grant discovery, eligibility research, matching, and application support.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-geogrid"><strong>legends-geogrid</strong></a></td><td valign="top">Local Maps SEO</td><td valign="top">Open-source Google Maps rank checker: geographic search grids, local visibility matrices, street maps, and actionable client reports at raw DataForSEO cost.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-dataforseo-kit"><strong>legends-dataforseo</strong></a></td><td valign="top">Search Data Engine</td><td valign="top">High-throughput Python client and CLI for DataForSEO: SERP queues, keyword research, official API discovery, and reusable evidence export. No MCP server required.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-github"><strong>legends-github</strong></a></td><td valign="top">Repo Optimization</td><td valign="top">Repository optimization suite for Claude, Codex, and Gemini. Audits repos, improves README copy, tunes metadata, manages releases, and ensures community health.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-stable-audio-3"><strong>legends-stable-audio-3</strong></a></td><td valign="top">Audio Production</td><td valign="top">Agent-operated Stable Audio 3: hardware-aware batch planning, continuous audio mixes, custom adapters, and sound effect generation.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-obs-kit"><strong>legends-obs</strong></a></td><td valign="top">Video Recording</td><td valign="top">Agent-operated OBS Studio controller on Windows: hardware inspection, scene and encoder planning, rollback snapshots, verified recording pipelines, and optional cursor overlay extra.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/hyperyap"><strong>hyperyap</strong></a></td><td valign="top">Local Voice Typing</td><td valign="top">Native desktop dictation powered by NVIDIA Parakeet: app-focused paste, custom vocabulary, configurable shortcuts, and local transcription.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-firecrawl"><strong>legends-firecrawl</strong></a></td><td valign="top">Web Research</td><td valign="top">Unified Firecrawl web operations and Alexandria data intelligence with credit efficiency and automated IP safety routing.</td></tr>
<tr><td valign="top"><a href="https://github.com/avalonreset/legends-yt-dlp"><strong>legends-yt-dlp</strong></a></td><td valign="top">Video Capture</td><td valign="top">Repeatable yt-dlp source pulls, verification, transcripts, search, and clip-building with pacing, bulk guardrails, and optional Mullvad VPN.</td></tr>
</table>


---

<p align="center">
  <a href="https://www.youtube.com/watch?v=1StVdAvxehs"><img src="assets/greatest-marketer.webp" alt="the worlds greatest marketer makes a sales presentation" width="49.5%" /></a>
  <a href="assets/bizintel.webp"><img src="assets/bizintel.webp" alt="business intelligence: always has been" width="49.5%" /></a>
</p>

---

### Community & Resources

- **Website:** [cto-legends.com](https://cto-legends.com/)
- **Pro Community:** [AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro)
- **Free Community:** [AI Marketing Hub](https://www.skool.com/ai-marketing-hub)
- **YouTube:** [@avalonreset](https://www.youtube.com/@avalonreset)
- **LinkedIn:** [Benjamin Samar](https://www.linkedin.com/in/benjaminsamar/)
