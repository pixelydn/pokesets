"""
Gen 7 Battle Factory — HTML page generator
Usage:
    python generate_g7bf.py <path/to/factory-sets.json> <output_dir> [TIER1 TIER2 ...]

Examples:
    python generate_g7bf.py factory-sets.json ./out
        → generates ALL tiers found in the JSON

    python generate_g7bf.py factory-sets.json ./out PU LC Mono
        → generates only the specified tiers

Output structure:
    <output_dir>/
        styles.css              (copy of styles.css from same dir as this script)
        gen7/battle-factory/
            <Tier>/<slug>/index.html

Notes:
    - styles.css must be in the same directory as this script, or the output
      root, to be copied. If not found it is skipped with a warning.
    - HTML files reference ../../../../styles.css (4 levels up).
"""

import json
import os
import sys
import shutil
import zipfile

# ── Stat / nature lookup tables ──────────────────────────────────────────────

EV_MAP = {
    'hp': 'HP', 'atk': 'ATK', 'def': 'DEF',
    'spa': 'SPA', 'spd': 'SPD', 'spe': 'SPE',
}

NATURE_MOD = {
    'Hardy':   None, 'Docile':  None, 'Serious': None,
    'Bashful': None, 'Quirky':  None,
    'Lonely':  ('+Atk', '-Def'),  'Brave':   ('+Atk', '-Spe'),
    'Adamant': ('+Atk', '-SpA'),  'Naughty': ('+Atk', '-SpD'),
    'Bold':    ('+Def', '-Atk'),  'Relaxed': ('+Def', '-Spe'),
    'Impish':  ('+Def', '-SpA'),  'Lax':     ('+Def', '-SpD'),
    'Timid':   ('+Spe', '-Atk'),  'Hasty':   ('+Spe', '-Def'),
    'Jolly':   ('+Spe', '-SpA'),  'Naive':   ('+Spe', '-SpD'),
    'Modest':  ('+SpA', '-Atk'),  'Mild':    ('+SpA', '-Def'),
    'Quiet':   ('+SpA', '-Spe'),  'Rash':    ('+SpA', '-SpD'),
    'Calm':    ('+SpD', '-Atk'),  'Gentle':  ('+SpD', '-Def'),
    'Sassy':   ('+SpD', '-Spe'),  'Careful': ('+SpD', '-SpA'),
}

# ── Formatting helpers ────────────────────────────────────────────────────────

def fmt_list(arr):
    """Join a list of options with ' / ', treating empty strings as absent."""
    cleaned = [x for x in arr if x != '']
    return ' / '.join(str(x) for x in cleaned) if cleaned else '\u2014'


def fmt_nature(n):
    """Format a nature (string or list) with stat modifiers appended."""
    if isinstance(n, list):
        return ' / '.join(
            name + (' ({}, {})'.format(*NATURE_MOD[name]) if NATURE_MOD.get(name) else '')
            for name in n
        )
    mod = NATURE_MOD.get(n)
    return n + (' ({}, {})'.format(*mod) if mod else '')


def fmt_ev_iv(evs, ivs, level, happiness):
    """Build the combined EV / IV display string."""
    parts = []
    if level:
        parts.append('Lv ' + str(level))
    ev_str = ' / '.join(EV_MAP[k] + ' ' + str(v) for k, v in evs.items())
    if ev_str:
        parts.append(ev_str)
    if ivs:
        parts.append('[IVs: ' + ' / '.join(EV_MAP[k] + ' ' + str(v) for k, v in ivs.items()) + ']')
    if happiness is not None:
        parts.append('[Happiness: ' + str(happiness) + ']')
    return '  '.join(parts)


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def sprite_id(species):
    """
    Derive the Pokémon Showdown sprite filename stem from a species name.
    e.g. 'Kommo-o' → 'kommoo', 'Mr. Mime' → 'mrmime', 'Type: Null' → 'typenull'
    """
    s = species.lower().replace(' ', '').replace('.', '').replace(':', '')
    if s.endswith('-o'):
        s = s[:-2] + 'o'
    return s

# ── HTML builder ──────────────────────────────────────────────────────────────

def make_html(species, sets, tier):
    sid = sprite_id(species)
    sprite_url = 'https://play.pokemonshowdown.com/sprites/gen5/{}.png'.format(sid)

    cards = ''
    for s in sets:
        moves = s.get('moves', [])
        move_rows = ''.join(
            '<div class="row">'
            '<span class="row-label">Move {}</span>'
            '<span class="row-value">{}</span>'
            '</div>'.format(i + 1, esc(fmt_list(slot)))
            for i, slot in enumerate(moves)
        )

        ev_iv = fmt_ev_iv(
            s.get('evs', {}),
            s.get('ivs'),
            s.get('level'),
            s.get('happiness'),
        )

        stat_rows = (
            '<div class="row"><span class="row-label">Item</span>'
            '<span class="row-value">{}</span></div>'
            '<div class="row"><span class="row-label">Ability</span>'
            '<span class="row-value">{}</span></div>'
            '<div class="row"><span class="row-label">Nature</span>'
            '<span class="row-value">{}</span></div>'
            '<div class="row"><span class="row-label">EV / IV</span>'
            '<span class="row-value">{}</span></div>'
        ).format(
            esc(fmt_list(s.get('item', []))),
            esc(fmt_list(s.get('ability', []))),
            esc(fmt_nature(s.get('nature', ''))),
            esc(ev_iv),
        )

        cards += (
            '<div class="set-block"><div class="set-inner">'
            '<div class="set-moves">{}</div>'
            '<div class="set-stats">{}</div>'
            '</div></div>\n'
        ).format(move_rows, stat_rows)

    return '\n'.join([
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        '  <title>{} \u2014 Gen 7 Battle Factory</title>'.format(esc(species)),
        '  <link rel="stylesheet" href="../../../../styles.css">',
        '</head>',
        '<body class="g7bf">',
        '  <a class="back-link" href="../">\u2190 {}</a>'.format(esc(tier)),
        '  <div class="page-header">',
        '    <img class="sprite" src="{}" alt="{}" onerror="this.setAttribute(\'data-broken\',1)">'.format(
            sprite_url, esc(species)),
        '    <div class="name-block">',
        '      <h1>{}</h1>'.format(esc(species)),
        '      <p class="subtitle">Gen 7 Battle Factory \u2014 {}</p>'.format(esc(tier)),
        '    </div>',
        '  </div>',
        '  <p class="sets-label">Set(s):</p>',
        cards,
        '</body>',
        '</html>',
    ])

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    json_path  = sys.argv[1]
    output_dir = sys.argv[2]
    tiers_arg  = sys.argv[3:]

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    tiers = tiers_arg if tiers_arg else list(data.keys())
    missing = [t for t in tiers if t not in data]
    if missing:
        print('WARNING: tiers not found in JSON:', missing)
        tiers = [t for t in tiers if t in data]

    total = 0
    for tier in tiers:
        for slug, mon_data in data[tier].items():
            species = mon_data['sets'][0]['species']
            html    = make_html(species, mon_data['sets'], tier)
            rel     = os.path.join('gen7', 'battle-factory', tier, slug, 'index.html')
            full    = os.path.join(output_dir, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8') as fh:
                fh.write(html)
            total += 1

    # Copy styles.css if available
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    css_src     = os.path.join(script_dir, 'styles.css')
    css_dst     = os.path.join(output_dir, 'styles.css')
    if os.path.exists(css_src):
        shutil.copy(css_src, css_dst)
        print('Copied styles.css →', css_dst)
    else:
        print('WARNING: styles.css not found next to script — skipped.')

    print('Generated {} HTML files across {} tier(s): {}'.format(
        total, len(tiers), ', '.join(tiers)))

    # Optional: zip the output
    zip_path = output_dir.rstrip('/\\') + '.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for fname in files:
                fp = os.path.join(root, fname)
                zf.write(fp, os.path.relpath(fp, output_dir))
    print('Zipped →', zip_path)


if __name__ == '__main__':
    main()