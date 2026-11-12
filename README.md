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
