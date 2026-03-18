"""
Gen 9 Battle Factory — HTML page generator
Usage:
    python generate_g9bf.py <path/to/factory-sets.json> <output_dir> [TIER1 TIER2 ...]

Output structure:
    <output_dir>/
        styles.css
        gen9/battle-factory/<Tier>/<slug>/index.html

Gen 9 extras vs gen 7/8:
    - teraType      : list of possible Tera types, shown as pills in the header
    - wantsTera     : True if the set actively wants to terastallize
    - set weight    : already sums to 100 per mon → displayed as a % badge on each card
    - mon weight    : relative within tier → calculated as % of tier total
    - gender        : shown in extra chip row when present
"""

import json, os, sys, re, shutil

# ── Type lookup (base types + gen9 new mons) ──────────────────────────────────

TYPES = {
    'abomasnow':['Grass','Ice'],'absol':['Dark'],'accelgor':['Bug'],
    'aegislash':['Steel','Ghost'],'aerodactyl':['Rock','Flying'],
    'aggron':['Steel','Rock'],'alakazam':['Psychic'],'alomomola':['Water'],
    'amaura': ['Rock', 'Ice'],
    'altaria':['Dragon','Flying'],'ambipom':['Normal'],'amoonguss':['Grass','Poison'],
    'ampharos':['Electric'],'araquanid':['Water','Bug'],'arcanine':['Fire'],
    'arceus':['Normal'],'arceus-dark':['Dark'],'arceus-dragon':['Dragon'],
    'arceus-electric':['Electric'],'arceus-fairy':['Fairy'],'arceus-flying':['Flying'],
    'arceus-ghost':['Ghost'],'arceus-grass':['Grass'],'arceus-ground':['Ground'],
    'arceus-poison':['Poison'],'arceus-rock':['Rock'],'arceus-steel':['Steel'],
    'arceus-water':['Water'],'archen':['Rock','Flying'],'archeops':['Rock','Flying'],
    'arctovish':['Water','Ice'],'armarouge':['Fire','Psychic'],
    'articuno':['Ice','Flying'],'articuno-galar':['Psychic','Flying'],
    'audino':['Normal'],'aurorus':['Rock','Ice'],'avalugg':['Ice'],
    'azelf':['Psychic'],'azumarill':['Water','Fairy'],
    'barbaracle':['Rock','Water'],'basculegion':['Water','Ghost'],
    'basculegion-f':['Water','Ghost'],
    'beartic':['Ice'],'beedrill':['Bug','Poison'],'bellossom':['Grass'],
    'bellibolt':['Electric'],'bewear':['Normal','Fighting'],'bisharp':['Dark','Steel'],
    'blacephalon':['Fire','Ghost'],'blastoise':['Water'],'blaziken':['Fire','Fighting'],
    'blissey':['Normal'],'bombirdier':['Flying','Dark'],
    'brambleghast':['Grass','Ghost'],'braviary':['Normal','Flying'],
    'braviary-hisui':['Psychic','Flying'],'breloom':['Grass','Fighting'],
    'bronzong':['Steel','Psychic'],'bruxish':['Water','Psychic'],
    'bulbasaur': ['Grass', 'Poison'],
    'buneary': ['Normal'],
    'bunnelby': ['Normal'],
    'buzzwole':['Bug','Fighting'],
    'cacturne':['Grass','Dark'],'calyrex-ice':['Psychic','Ice'],
    'calyrex-shadow':['Psychic','Ghost'],'camerupt':['Fire','Ground'],
    'carracosta':['Water','Rock'],'celebi':['Psychic','Grass'],
    'celesteela':['Steel','Flying'],'centiskorch':['Fire','Bug'],
    'chandelure':['Ghost','Fire'],'chansey':['Normal'],'charizard':['Fire','Flying'],
    'chesnaught':['Grass','Fighting'],'chien-pao':['Dark','Ice'],
    'chinchou':['Water','Electric'],'cinccino':['Normal'],
    'cinderace':['Fire'],'clefable':['Fairy'],'clefairy':['Fairy'],
    'clodsire':['Poison','Ground'],'cloyster':['Water','Ice'],
    'coalossal':['Rock','Fire'],'cobalion':['Steel','Fighting'],
    'cofagrigus':['Ghost'],'conkeldurr':['Fighting'],'copperajah':['Steel'],
    'corviknight':['Flying','Steel'],'cramorant':['Flying','Water'],
    'crabominable':['Fighting','Ice'],'cradily':['Rock','Grass'],
    'crawdaunt':['Water','Dark'],'cresselia':['Psychic'],'crobat':['Poison','Flying'],
    'cryogonal':['Ice'],'cyclizar':['Dragon','Normal'],
    'darkrai':['Dark'],'darmanitan':['Fire'],'darmanitan-galar':['Ice'],
    'decidueye':['Grass','Ghost'],'decidueye-hisui':['Grass','Fighting'],
    'delphox':['Fire','Psychic'],'deoxys-attack':['Psychic'],
    'deoxys-defense':['Psychic'],'deoxys-speed':['Psychic'],
    'dhelmise':['Ghost','Grass'],'dialga':['Steel','Dragon'],
    'diancie':['Rock','Fairy'],'diggersby':['Normal','Ground'],
    'ditto':['Normal'],'dondozo':['Water'],'donphan':['Ground'],
    'doublade':['Steel','Ghost'],'dragalge':['Poison','Dragon'],
    'dragapult':['Dragon','Ghost'],'dragonite':['Dragon','Flying'],
    'drampa':['Normal','Dragon'],'drapion':['Poison','Dark'],
    'dudunsparce':['Normal'],'duraludon':['Steel','Dragon'],'durant':['Bug','Steel'],
    'eelektross':['Electric'],'electrode-hisui':['Electric','Grass'],
    'emboar':['Fire','Fighting'],'empoleon':['Water','Steel'],
    'enamorus':['Fairy','Flying'],'enamorus-therian':['Fairy','Flying'],
    'entei':['Fire'],'escavalier':['Bug','Steel'],'espeon':['Psychic'],
    'eternatus':['Poison','Dragon'],'excadrill':['Ground','Steel'],
    'exeggutor':['Grass','Psychic'],'exeggutor-alola':['Grass','Dragon'],
    'farfetchd-galar':['Fighting'],'feraligatr':['Water'],
    'ferrothorn':['Grass','Steel'],'fezandipiti':['Poison','Fairy'],
    'floatzel':['Water'],'florges':['Fairy'],'fluttermane':['Ghost','Fairy'],
    'flygon':['Ground','Dragon'],'forretress':['Bug','Steel'],
    'froslass':['Ice','Ghost'],'frosmoth':['Ice','Bug'],
    'gallade':['Psychic','Fighting'],'galvantula':['Bug','Electric'],
    'garbodor':['Poison'],'garchomp':['Dragon','Ground'],
    'gardevoir':['Psychic','Fairy'],'garganacl':['Rock'],
    'gastrodon':['Water','Ground'],'gengar':['Ghost','Poison'],
    'gholdengo':['Steel','Ghost'],'gigalith':['Rock'],
    'giratina':['Ghost','Dragon'],'giratina-origin':['Ghost','Dragon'],
    'glalie':['Ice'],'glastrier':['Ice'],'gligar':['Ground','Flying'],
    'glimmora':['Rock','Poison'],'gliscor':['Ground','Flying'],
    'golbat':['Poison','Flying'],'golem':['Rock','Ground'],
    'golisopod':['Bug','Water'],'golurk':['Ground','Ghost'],
    'goodra':['Dragon'],'goodra-hisui':['Steel','Dragon'],
    'gothitelle':['Psychic'],'great-tusk':['Ground','Fighting'],
    'greattusk':['Ground','Fighting'],'greninja':['Water','Dark'],
    'greninja-bond':['Water','Dark'],'grimmsnarl':['Dark','Fairy'],
    'grimer-alola': ['Poison', 'Dark'],
    'gyarados':['Water','Flying'],
    'hariyama':['Fighting'],'hatterene':['Psychic','Fairy'],
    'haunter':['Ghost','Poison'],'hawlucha':['Fighting','Flying'],
    'haxorus':['Dragon'],'heatran':['Fire','Steel'],
    'heracross':['Bug','Fighting'],'hippowdon':['Ground'],
    'ho-oh':['Fire','Flying'],'honchkrow':['Dark','Flying'],
    'hoopa':['Psychic','Ghost'],'hoopa-unbound':['Psychic','Dark'],
    'houndoom':['Dark','Fire'],'hydrapple':['Grass','Dragon'],
    'hydreigon':['Dark','Dragon'],
    'incineroar':['Fire','Dark'],'infernape':['Fire','Fighting'],
    'inteleon':['Water'],'iron-bundle':['Ice','Water'],
    'iron-crown':['Steel','Psychic'],'iron-moth':['Fire','Poison'],
    'iron-valiant':['Fairy','Fighting'],'ironbundle':['Ice','Water'],
    'ironcrown':['Steel','Psychic'],'ironmoth':['Fire','Poison'],
    'ironvaliant':['Fairy','Fighting'],
    'jellicent':['Water','Ghost'],'jirachi':['Steel','Psychic'],
    'kartana':['Grass','Steel'],'keldeo':['Water','Fighting'],
    'kilowattrel':['Electric','Flying'],'kingambit':['Dark','Steel'],
    'kleavor':['Bug','Rock'],'klefki':['Steel','Fairy'],
    'kommoo':['Dragon','Fighting'],'koraidon':['Fighting','Dragon'],
    'krookodile':['Ground','Dark'],'kyogre':['Water'],
    'kyurem':['Dragon','Ice'],'kyurem-black':['Dragon','Ice'],
    'kyurem-white':['Dragon','Ice'],
    'landorus':['Ground','Flying'],'landorus-therian':['Ground','Flying'],
    'latias':['Dragon','Psychic'],'latios':['Dragon','Psychic'],
    'lilligant-hisui':['Grass','Fighting'],'lokix':['Bug','Dark'],
    'lopunny':['Normal'],'lucario':['Fighting','Steel'],
    'magneton':['Electric','Steel'],'magnezone':['Electric','Steel'],
    'mamoswine':['Ice','Ground'],'manaphy':['Water'],
    'mandibuzz':['Dark','Flying'],'manectric':['Electric'],
    'mantine':['Water','Flying'],'marshadow':['Fighting','Ghost'],
    'maushold':['Normal'],'meloetta':['Normal','Psychic'],
    'meowscarada':['Grass','Dark'],'mesprit':['Psychic'],
    'metagross':['Steel','Psychic'],'mienshao':['Fighting'],
    'milotic':['Water'],'mimikyu':['Ghost','Fairy'],
    'moltres':['Fire','Flying'],'moltres-galar':['Dark','Flying'],
    'mudsdale':['Ground'],'muk-alola':['Poison','Dark'],
    'munkidori':['Poison','Psychic'],
    'naclstack':['Rock'],'naganadel':['Poison','Dragon'],
    'necrozma':['Psychic'],'necrozma-dusk-mane':['Psychic','Steel'],
    'necrozma-dawn-wings':['Psychic','Ghost'],
    'nidoking':['Poison','Ground'],'nidoqueen':['Poison','Ground'],
    'nihilego':['Rock','Poison'],'ninetales':['Fire'],
    'ninetales-alola':['Ice','Fairy'],'noivern':['Flying','Dragon'],
    'ogerpon':['Grass'],'ogerpon-cornerstone':['Grass','Rock'],
    'ogerpon-wellspring':['Grass','Water'],
    'okidogi':['Poison','Fighting'],'oricorio':['Fire','Flying'],
    'oricorio-pom-pom':['Electric','Flying'],'orthworm':['Steel'],
    'overqwil':['Dark','Poison'],
    'palkia':['Water','Dragon'],'palossand':['Ghost','Ground'],
    'pawmot':['Electric','Fighting'],'pecharunt':['Poison','Ghost'],
    'pelipper':['Water','Flying'],'Persian-alola':['Dark'],
    'persian-alola':['Dark'],'porygon-z':['Normal'],'porygon2':['Normal'],
    'primarina':['Water','Fairy'],'qwilfish':['Water','Poison'],
    'qwilfish-hisui':['Dark','Poison'],
    'ragingbolt':['Electric','Dragon'],'raikou':['Electric'],
    'rayquaza':['Dragon','Flying'],'registeel':['Steel'],
    'reuniclus':['Psychic'],'revavroom':['Steel','Poison'],
    'rhydon':['Ground','Rock'],'rhyperior':['Ground','Rock'],
    'rillaboom':['Grass'],'roaring-moon':['Dragon','Dark'],
    'roaringmoon':['Dragon','Dark'],'roserade':['Grass','Poison'],
    'rotom-heat':['Electric','Fire'],'rotom-mow':['Electric','Grass'],
    'rotom-wash':['Electric','Water'],
    'sableye':['Dark','Ghost'],'salamence':['Dragon','Flying'],
    'salazzle':['Poison','Fire'],'samurott-hisui':['Water','Dark'],
    'sandaconda':['Ground'],'sandslash-alola':['Ice','Steel'],
    'sandyshocks':['Electric','Ground'],'scizor':['Bug','Steel'],
    'scrafty':['Dark','Fighting'],'screamtail':['Fairy','Psychic'],
    'scyther':['Bug','Flying'],'serperior':['Grass'],
    'sinistcha':['Grass','Ghost'],'skarmory':['Steel','Flying'],
    'skeledirge':['Fire','Ghost'],'skuntank':['Poison','Dark'],
    'slitherwing':['Bug','Fighting'],'slowbro':['Water','Psychic'],
    'slowbro-galar':['Poison','Psychic'],'slowking':['Water','Psychic'],
    'slowking-galar':['Poison','Psychic'],'sneasel':['Dark','Ice'],
    'sneasel-hisui':['Fighting','Poison'],'suicune':['Water'],
    'swampert':['Water','Ground'],'sylveon':['Fairy'],
    'talonflame':['Fire','Flying'],'tatsugiri':['Dragon','Water'],
    'tauros-paldea-aqua':['Fighting','Water'],
    'tauros-paldea-blaze':['Fighting','Fire'],
    'tentacruel':['Water','Poison'],'terrakion':['Rock','Fighting'],
    'thundurus-therian':['Electric','Flying'],'ting-lu':['Dark','Ground'],
    'tinkaton':['Fairy','Steel'],'tinglu':['Dark','Ground'],
    'tornadus':['Flying'],'tornadus-therian':['Flying'],
    'torterra':['Grass','Ground'],'toxapex':['Poison','Water'],
    'toxicroak':['Poison','Fighting'],'toxtricity':['Electric','Poison'],
    'typhlosion-hisui':['Fire','Ghost'],'tyranitar':['Rock','Dark'],
    'umbreon':['Dark'],'ursaluna':['Ground','Normal'],
    'urshifu':['Fighting','Dark'],'urshifu-rapid-strike':['Fighting','Water'],
    'uxie':['Psychic'],
    'vaporeon':['Water'],'venusaur':['Grass','Poison'],'virizion':['Grass','Fighting'],
    'volcanion':['Fire','Water'],'volcarona':['Bug','Fire'],
    'weavile':['Dark','Ice'],'weezing-galar':['Poison','Fairy'],
    'whimsicott':['Grass','Fairy'],'wishiwashi':['Water'],
    'wo-chien':['Dark','Grass'],
    'xerneas':['Fairy'],'xurkitree':['Electric'],
    'yveltal':['Dark','Flying'],
    'zacian':['Fairy'],'zamazenta':['Fighting'],
    'zamazenta-crowned':['Fighting','Steel'],
    'zapdos':['Electric','Flying'],'zapdos-galar':['Fighting','Flying'],
    'zarude':['Dark','Grass'],'zekrom':['Dragon','Electric'],
    'zeraora':['Electric'],'zoroark':['Dark'],
    'zoroark-hisui':['Normal','Ghost'],
}

from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

def sprite_exists(url):
    try:
        req = urllib.request.Request(url, method='HEAD')
        urllib.request.urlopen(req, timeout=5)
        return True
    except:
        return False

def check_sprites(sids):
    """Returns {sid: (front_url, back_url)} using gif if available, png fallback otherwise."""
    base   = SPRITE_BASE
    tasks  = {}
    result = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        for sid in sids:
            front_gif = base + '/gen5ani/' + sid + '.gif'
            back_gif  = base + '/gen5ani-back/' + sid + '.gif'
            static    = base + '/gen5/' + sid + '.png'
            tasks[pool.submit(sprite_exists, front_gif)] = ('front', sid, front_gif, static)
            tasks[pool.submit(sprite_exists, back_gif)]  = ('back',  sid, back_gif,  static)

        for future in as_completed(tasks):
            kind, sid, gif, static = tasks[future]
            url = gif if future.result() else static
            if sid not in result:
                result[sid] = [None, None]
            if kind == 'front':
                result[sid][0] = url
            else:
                result[sid][1] = url

    return {sid: (urls[0], urls[1]) for sid, urls in result.items()}


SPRITE_BASE = 'https://play.pokemonshowdown.com/sprites'
ITEM_BASE   = 'https://play.pokemonshowdown.com/sprites/itemicons'

# ── Lookup tables ─────────────────────────────────────────────────────────────

EV_MAP = {
    'hp':'HP','atk':'ATK','def':'DEF','spa':'SPA','spd':'SPD','spe':'SPE',
}

NATURE_MOD = {
    'Hardy':None,'Docile':None,'Serious':None,'Bashful':None,'Quirky':None,
    'Lonely':('+Atk','-Def'),'Brave':('+Atk','-Spe'),'Adamant':('+Atk','-SpA'),'Naughty':('+Atk','-SpD'),
    'Bold':('+Def','-Atk'),'Relaxed':('+Def','-Spe'),'Impish':('+Def','-SpA'),'Lax':('+Def','-SpD'),
    'Timid':('+Spe','-Atk'),'Hasty':('+Spe','-Def'),'Jolly':('+Spe','-SpA'),'Naive':('+Spe','-SpD'),
    'Modest':('+SpA','-Atk'),'Mild':('+SpA','-Def'),'Quiet':('+SpA','-Spe'),'Rash':('+SpA','-SpD'),
    'Calm':('+SpD','-Atk'),'Gentle':('+SpD','-Def'),'Sassy':('+SpD','-Spe'),'Careful':('+SpD','-SpA'),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def sprite_id(species):
    s = species.lower().replace(' ','').replace('.','').replace(':','').replace("'",'')
    if s.endswith('-o'): s = s[:-2]+'o'
    return s

def item_id(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

def fmt_list(arr):
    cleaned = [x for x in arr if x != '']
    return ' / '.join(str(x) for x in cleaned) if cleaned else '\u2014'

def fmt_nature(n):
    if isinstance(n, list):
        return ' / '.join(
            name+(' ({}, {})'.format(*NATURE_MOD[name]) if NATURE_MOD.get(name) else '')
            for name in n)
    mod = NATURE_MOD.get(n)
    return n+(' ({}, {})'.format(*mod) if mod else '')

def fmt_evs(evs, happiness):
    ev_str = ' / '.join(EV_MAP[k]+' '+str(v) for k,v in evs.items())
    if happiness is not None:
        ev_str += '  [Happiness: {}]'.format(happiness)
    return ev_str

def fmt_ivs(ivs):
    if not ivs:
        return None
    return ' / '.join(EV_MAP[k]+' '+str(v) for k,v in ivs.items())

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def row(label, value):
    return (
        '<div class="row"><span class="row-label">{}</span>'
        '<span class="row-value">{}</span></div>'
    ).format(label, value)

def item_html(items):
    cleaned = [x for x in items if x != '']
    if not cleaned:
        return '\u2014'
    parts = []
    for it in cleaned:
        src  = ITEM_BASE + '/' + item_id(it) + '.png'
        icon = '<img class="item-icon" src="' + src + '" onerror="this.remove()" alt="">'
        parts.append(icon + esc(it))
    return ' / '.join(parts)

def type_badges_html(sid):
    types = TYPES.get(sid, [])
    if not types:
        return ''
    spans = ''.join(
        '<span class="type-badge type-{slug}">{name}</span>'.format(
            slug=t.lower(), name=t.upper())
        for t in types
    )
    return '<div class="type-badges">{}</div>'.format(spans)

def tera_type_pills(tera_types, wants_tera):
    if not tera_types:
        return '—'
    star = ' ★' if wants_tera else ''
    spans = ''.join(
        '<span class="type-badge type-' + t.lower() + '">'
        + t.upper() + '</span>'
        for t in tera_types
    )
    if star:
        spans += '<span class="tera-star">' + star.strip() + '</span>'
    return spans


def make_html(species, sets, tier, mon_weight_pct):
    sid        = sprite_id(species)
    front_url  = '{}/gen5ani/{}.gif'.format(SPRITE_BASE, sid)
    back_url   = '{}/gen5ani-back/{}.gif'.format(SPRITE_BASE, sid)
    static_url = '{}/gen5/{}.png'.format(SPRITE_BASE, sid)

    sprite_tag = (
        '<img class="sprite"'
        ' src="{front}" data-front="{front}" data-back="{back}"'
        
        
        ' onerror="this.onerror=null;this.src=\'{static}\';'
        'this.onmouseover=null;this.onmouseout=null"'
        ' alt="{name}">'
    ).format(front=front_url, back=back_url, name=esc(species))

    cards = ''
    for s in sets:
        level      = s.get('level')
        moves      = s.get('moves', [])
        ivs        = s.get('ivs')
        happiness  = s.get('happiness')
        set_weight = s.get('weight')      # already % (sums to 100)
        tera_types = s.get('teraType', [])
        wants_tera = s.get('wantsTera')
        gender     = s.get('gender')

        # Moves column — 4 move rows + set frequency as 5th row
        move_rows = ''.join(
            row('Move {}'.format(i+1), esc(fmt_list(slot)))
            for i, slot in enumerate(moves)
        )
        freq_label = '{}%'.format(set_weight) if set_weight is not None else '—'
        move_rows += row('Frequency', freq_label)

        # Stats column — Item / Ability / Nature / EVs / Tera (always 5 rows)
        iv_str = fmt_ivs(ivs)
        tera_value = tera_type_pills(tera_types, wants_tera)
        stat_rows = (
            '<div class="row"><span class="row-label">Item</span>'
            '<span class="row-value">{}</span></div>'.format(item_html(s.get('item',[]))) +
            row('Ability', esc(fmt_list(s.get('ability',[])))) +
            row('Nature',  esc(fmt_nature(s.get('nature','')))) +
            row('EVs',     esc(fmt_evs(s.get('evs',{}), happiness))) +
            '<div class="row"><span class="row-label">Tera</span>'
            '<span class="row-value">{}</span></div>'.format(tera_value)
        )

        # 6th row — only when IVs or level present
        extra_tags = []
        if level:
            extra_tags.append('Lv {}'.format(level))
        if iv_str:
            extra_tags.append('IVs: {}'.format(iv_str))
        if gender:
            extra_tags.append(gender)

        extra_html = ''
        if extra_tags:
            chips = ''.join(
                '<span class="extra-chip">{}</span>'.format(t)
                for t in extra_tags
            )
            extra_html = '<div class="set-extra">{}</div>'.format(chips)

        cards += (
            '<div class="set-block">'
            '<div class="set-inner">'
            '<div class="set-moves">{moves}</div>'
            '<div class="set-stats">{stats}</div>'
            '</div>{extra}'
            '</div>\n'
        ).format(moves=move_rows, stats=stat_rows, extra=extra_html)


    return '\n'.join([
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        '  <title>{} \u2014 Gen 9 Battle Factory</title>'.format(esc(species)),
        '  <link rel="stylesheet" href="../../../../styles.css">',
        '</head>',
        '<body class="g9bf">',
        '  <a class="back-link" href="../">\u2190 {}</a>'.format(esc(tier)),
        '  <div class="page-header">',
        '    {}'.format(sprite_tag),
        '    <div class="name-block">',
        '      <h1>{}</h1>'.format(esc(species)),
        '      {}'.format(type_badges_html(sid)),
        '      <p class="subtitle">Gen 9 Battle Factory \u2014 {}</p>'.format(esc(tier)),
        '      <p class="mon-weight">Tier frequency: {}%</p>'.format(mon_weight_pct),
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
        # Pre-calculate mon-level pick rate % within this tier
        tier_weight_total = sum(mon.get('weight', 1) for mon in data[tier].values())

        for slug, mon_data in data[tier].items():
            species      = mon_data['sets'][0]['species']
            mon_weight   = mon_data.get('weight', 1)
            mon_pct      = round(mon_weight / tier_weight_total * 100, 1)

            html = make_html(species, mon_data['sets'], tier, mon_pct)
            rel  = os.path.join('gen9', 'battle-factory', tier, slug, 'index.html')
            full = os.path.join(output_dir, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8') as fh:
                fh.write(html)
            total += 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    css_src    = os.path.join(script_dir, 'styles.css')
    css_dst    = os.path.join(output_dir, 'styles.css')
    if os.path.exists(css_src):
        shutil.copy(css_src, css_dst)
        print('Copied styles.css \u2192', css_dst)
    else:
        print('WARNING: styles.css not found \u2014 skipped.')

    print('Generated {} files across {} tier(s): {}'.format(
        total, len(tiers), ', '.join(tiers)))

if __name__ == '__main__':
    main()
