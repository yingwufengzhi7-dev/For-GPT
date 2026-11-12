# Blender 3D Toolkit for Work

This repository tracks two complete upstream 3D tool projects:

- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) — Blender add-on and MCP server.
- [Blender Skills](https://github.com/arjun988/blender-skills) — modeling and procedural workflows.

Both are stored as **Git submodules** in `external/`, pinned to upstream revisions.

## Get both projects

```bash
git clone --recurse-submodules https://github.com/yingwufengzhi7-dev/For-GPT.git
# If already cloned:
git submodule update --init --recursive
```

## What this does not do

Storing code here does NOT install an add-on to Blender or connect a running Blender instance to ChatGPT Work. In a compatible Blender + MCP environment, consult `external/mcp-for-blender/README.md` for installation and connection instructions. The skills in `external/blender-skills/.claude/skills/` are instructions for an agent.

No private OC reference images, scene files, API keys or other personal project data are published in this repository.

## Tested headless runtime

This repository now provides an adapter for environments without a Blender GUI.
It uses the pinned upstream add-on and MCP server, with a main-thread command
queue pump, an owned Blender child process, and a private loopback port.

Requirements: Blender (tested 4.3.2), Python 3.10+, `mcp>=1.26,<2`, `httpx>=0.27`,
and `requests` in Blender's Python. Initialize both submodules first.

```bash
python scripts/check_connection.py
# STDIO server for a compatible MCP client:
python scripts/run_mcp.py --headless
```

`--headless` creates a fresh disposable scene. To continue an existing project,
load its .blend with `bpy.ops.wm.open_mainfile` through `execute_blender_code`, then
save changes under a new filename. The owned process exits with the MCP session;
unsaved scene edits are lost. Keep one client session open throughout editing.
Camera renders work in background mode; viewport/UI features require GUI Blender.
Without `--headless`, the launcher connects to an already-running add-on using
`BLENDER_HOST` and `BLENDER_PORT`.

Upstream excludes `blender_mcp/config.py` from its Git checkout. The launcher
supplies disabled telemetry configuration to avoid status-query failures. It does
not provide credentials or enable third-party asset services.

The full integration test checks MCP initialization/tool listing, add-on status,
mesh creation, evaluated Geometry Nodes output and cleanup. It modifies only its
owned disposable scene. A successful CLI test does not automatically add a tool
to an already-open ChatGPT conversation.

## Modeling workflows

`scripts/prepare_skills.py` prepares `blender-modeler` and `geometry-nodes` in the
personal-skills checkout. It bundles shared references, supports MCP or direct
Blender Python, corrects Blender 4.x compatibility guidance, and requires camera
verification in background mode. It refuses to overwrite an existing named skill.
Validate and save each prepared skill through the personal-skills workflow before
claiming installation. The upstream submodules remain unchanged.
