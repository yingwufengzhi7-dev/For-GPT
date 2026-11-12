"""Prepare the two modeling workflows in the user's personal-skills checkout."""
from pathlib import Path
import os
import shutil
import re
root = Path(__file__).resolve().parents[1]
source = root / 'external/blender-skills/.claude/skills'
target = Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))) / 'skills/remote-skills'
for name in ('blender-modeler', 'geometry-nodes'):
    existing = [p.parent for p in target.glob('*/SKILL.md') if re.search(r'^name: '+name+r'\s*$', p.read_text(), re.M)]
    if existing:
        raise SystemExit(f'Already installed: {name}; review existing skill before replacing')
    dest = target/name
    shutil.copytree(source/name, dest)
    shutil.copytree(source/'references', dest/'references/shared', dirs_exist_ok=True)
    shutil.copy2(root/'external/blender-skills/LICENSE', dest/'LICENSE.txt')
    path = dest/'SKILL.md'
    text = path.read_text()
    _, front, body = text.split('---', 2)
    description = re.search(r'^description: (.*)$', front, re.M).group(1)
    description = description.replace(' via MCP', ' with MCP or Blender Python')
    body = body.replace('../references/', 'references/shared/')
    body = body.replace('Preferred order (bottom to top)', 'Typical evaluation order (top to bottom; adapt to the object)')
    body = body.replace('- Enable Auto Smooth with appropriate angle (30°–60° hard surface)', '- On Blender 4.1+, use smooth-by-angle/sharp-edge workflows; do not use the removed mesh.use_auto_smooth property.')
    body = body.replace('- Expose seed and density as inputs', '- Expose seed and density for scatter systems; expose shape-specific parameters for curves and surfaces')
    adapter = '''\n## Execution compatibility\n\nInspect the available runtime before execution. Use working MCP tools when exposed, or a tested Python MCP client connected to the upstream server. If no MCP connection is available, execute Blender Python with the existing Blender binary instead of inventing tool names. Report which path actually ran.\n\nFor headless Blender, use camera renders for verification; viewport capture requires a GUI. Continue an existing .blend when provided and save edits to a new version. Compare front, three-quarter, side and rear cameras in the same scene for spatial design tasks. Separate geometric consistency from fidelity to the user's reference.\n\nOn Blender 4.x create Geometry Nodes sockets with node_group.interface.new_socket. Inspect actual node socket names and validate evaluated geometry. Do not assume a legacy API exists.\n\nThe upstream projects may use different MCP tool names across revisions. List the live tools and read schemas before calling them; examples in shared references are conceptual. Tool availability is not implied by installation of this skill.\n\n'''
    path.write_text('---\nname: '+name+'\ndescription: '+description+'\n---\n'+adapter+body)
    # Replace the shared transport guide so it does not forbid a working local runtime.
    (dest/'references/shared/mcp-integration.md').write_text('''# Blender execution\n\nRead the installed server tool catalog and schemas. Prefer a verified MCP connection. If unavailable, run bpy through the existing Blender binary. Do not substitute UI instructions when local execution is possible. For background mode use camera renders, not viewport screenshots. Validate results and save a new scene version.\n''')
    print(dest)
