"""
Checks which pokemon are missing animated sprites on Showdown.
Outputs missing front gifs, missing back gifs, and missing both.

Usage:
    python check_sprites.py <factory-sets.json> [more.json ...]

Example:
    python check_sprites.py gen7.json gen8.json gen9.json
"""

import json, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

SPRITE = 'https://play.pokemonshowdown.com/sprites'

SPRITE_ID_EXCEPTIONS = {'porygon-z': 'porygonz'}

def sprite_id(species):
    s = species.lower().replace(' ','').replace('.','').replace(':','').replace("'",'')
    if s.endswith('-o'):
        s = s[:-2] + 'o'
    return SPRITE_ID_EXCEPTIONS.get(s, s)

def url_exists(url):
    try:
        req = urllib.request.Request(url, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    species_map = {}
    for path in sys.argv[1:]:
        data = json.loads(open(path, encoding='utf-8').read())
        for tier in data:
            for slug, mon in data[tier].items():
                name = mon['sets'][0]['species']
                sid  = sprite_id(name)
                species_map[sid] = name

    total = len(species_map)
    print(f'Checking {total} species...', flush=True)

    tasks = {}
    results = {}
    with ThreadPoolExecutor(max_workers=20) as pool:
        for sid in species_map:
            front = SPRITE + '/gen5ani/' + sid + '.gif'
            back  = SPRITE + '/gen5ani-back/' + sid + '.gif'
            tasks[pool.submit(url_exists, front)] = ('front', sid)
            tasks[pool.submit(url_exists, back)]  = ('back',  sid)

        done = 0
        for future in as_completed(tasks):
            kind, sid = tasks[future]
            if sid not in results:
                results[sid] = {}
            results[sid][kind] = future.result()
            done += 1
            print(f'\r  {done}/{total*2} checks done', end='', flush=True)

    print()

    no_front, no_back, no_both = [], [], []
    for sid, res in results.items():
        has_front = res.get('front', False)
        has_back  = res.get('back',  False)
        name = species_map[sid]
        if not has_front and not has_back:
            no_both.append(name)
        elif not has_front:
            no_front.append(name)
        elif not has_back:
            no_back.append(name)

    if no_both:
        print(f'\n=== Missing BOTH front + back ({len(no_both)}) ===')
        for n in sorted(no_both): print(f'  {n}')

    if no_front:
        print(f'\n=== Missing FRONT gif only ({len(no_front)}) ===')
        for n in sorted(no_front): print(f'  {n}')

    if no_back:
        print(f'\n=== Missing BACK gif only ({len(no_back)}) ===')
        for n in sorted(no_back): print(f'  {n}')

    if not no_both and not no_front and not no_back:
        print('All sprites present!')
    else:
        print(f'\nPNG fallback base: {SPRITE}/gen5/<id>.png')

if __name__ == '__main__':
    main()
