from pathlib import Path

root = Path(__file__).parent
# Match the intrinsic widths of the lower table's heading artwork.
for width in (240, 720):
    (root / f'assets/column-width-{width}.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="1" viewBox="0 0 {width} 1"></svg>\n', encoding='utf-8')
for filename in ('README.md', 'render-profile.py'):
    path=root/filename
    text=path.read_text(encoding='utf-8')
    text=text.replace('one skill to discover legends modules, load instructions, and check readiness.',
                      'discover legends modules, load workflows, check readiness.')
    text=text.replace('<strong><code>cto-legends</code></strong></a></td>',
        '<strong><code>cto-legends</code></strong></a><br/><img src="assets/column-width-240.svg" width="240" height="1" alt="" /></td>')
    text=text.replace('<strong>single-skill-router</strong></td>',
        '<strong>single-skill-router</strong><br/><img src="assets/column-width-240.svg" width="240" height="1" alt="" /></td>')
    text=text.replace('discover legends modules, load workflows, check readiness.</td>',
        'discover legends modules, load workflows, check readiness.<br/><img src="assets/column-width-720.svg" width="720" height="1" alt="" /></td>')
    path.write_text(text,encoding='utf-8')
print('Router intrinsic column widths now match header assets: 240 / 240 / 720.')
