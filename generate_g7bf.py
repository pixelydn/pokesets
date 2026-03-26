"""
Gen 7 Battle Factory — HTML page generator
Usage:
    python generate_g7bf.py <path/to/factory-sets.json> <output_dir> [TIER1 TIER2 ...]

Output structure:
    <output_dir>/
        styles.css
        gen7/battle-factory/<Tier>/<slug>/index.html
"""

import json, os, sys, re, shutil

# ── Type lookup ───────────────────────────────────────────────────────────────

TYPES = {
    'abomasnow':['Grass','Ice'],'abra':['Psychic'],'absol':['Dark'],
    'accelgor':['Bug'],'aegislash':['Steel','Ghost'],'aerodactyl':['Rock','Flying'],
    'aggron':['Steel','Rock'],'alakazam':['Psychic'],'alomomola':['Water'],
    'altaria':['Dragon','Flying'],'amaura':['Rock','Ice'],'amoonguss':['Grass','Poison'],
    'ampharos':['Electric'],'anorith':['Rock','Bug'],'araquanid':['Water','Bug'],
    'arcanine':['Fire'],'arceus':['Normal'],'arceus-dark':['Dark'],
    'arceus-dragon':['Dragon'],'arceus-electric':['Electric'],'arceus-fairy':['Fairy'],
    'arceus-flying':['Flying'],'arceus-ghost':['Ghost'],'arceus-grass':['Grass'],
    'arceus-ground':['Ground'],'arceus-poison':['Poison'],'arceus-rock':['Rock'],
    'arceus-steel':['Steel'],'arceus-water':['Water'],'archen':['Rock','Flying'],
    'archeops':['Rock','Flying'],'arctovish':['Water','Ice'],'armaldo':['Rock','Bug'],
    'aromatisse':['Fairy'],'articuno':['Ice','Flying'],'articuno-galar':['Psychic','Flying'],
    'audino':['Normal'],'aurorus':['Rock','Ice'],'avalugg':['Ice'],
    'azelf':['Psychic'],'azumarill':['Water','Fairy'],
    'barbaracle':['Rock','Water'],'beartic':['Ice'],'beedrill':['Bug','Poison'],
    'bellossom':['Grass'],'bewear':['Normal','Fighting'],'bisharp':['Dark','Steel'],
    'blacephalon':['Fire','Ghost'],'blastoise':['Water'],'blaziken':['Fire','Fighting'],
    'blissey':['Normal'],'braviary':['Normal','Flying'],'breloom':['Grass','Fighting'],
    'bronzong':['Steel','Psychic'],'bulbasaur':['Grass','Poison'],
    'buneary':['Normal'],'bunnelby':['Normal'],'buzzwole':['Bug','Fighting'],
    'cacturne':['Grass','Dark'],'calyrex-ice':['Psychic','Ice'],
    'calyrex-shadow':['Psychic','Ghost'],'camerupt':['Fire','Ground'],
    'carracosta':['Water','Rock'],'carvanha':['Water','Dark'],'celebi':['Psychic','Grass'],
    'celesteela':['Steel','Flying'],'centiskorch':['Fire','Bug'],'chandelure':['Ghost','Fire'],
    'chansey':['Normal'],'charizard':['Fire','Flying'],'chesnaught':['Grass','Fighting'],
    'chinchou':['Water','Electric'],'cinccino':['Normal'],'clamperl':['Water'],
    'clefable':['Fairy'],'clefairy':['Fairy'],'cloyster':['Water','Ice'],
    'coalossal':['Rock','Fire'],'cobalion':['Steel','Fighting'],'cofagrigus':['Ghost'],
    'combusken':['Fire','Fighting'],'comfey':['Fairy'],'conkeldurr':['Fighting'],
    'copperajah':['Steel'],'corphish':['Water'],'corviknight':['Flying','Steel'],
    'cottonee':['Grass','Fairy'],'crabominable':['Fighting','Ice'],'cradily':['Rock','Grass'],
    'crawdaunt':['Water','Dark'],'cresselia':['Psychic'],'croagunk':['Poison','Fighting'],
    'crobat':['Poison','Flying'],'cryogonal':['Ice'],
    'darkrai':['Dark'],'darmanitan':['Fire'],'darmanitan-galar':['Ice'],
    'decidueye':['Grass','Ghost'],'delphox':['Fire','Psychic'],'deoxys-attack':['Psychic'],
    'deoxys-defense':['Psychic'],'deoxys-speed':['Psychic'],'dhelmise':['Ghost','Grass'],
    'dialga':['Steel','Dragon'],'diancie':['Rock','Fairy'],'diggersby':['Normal','Ground'],
    'diglett':['Ground'],'ditto':['Normal'],'doduo':['Normal','Flying'],
    'donphan':['Ground'],'doublade':['Steel','Ghost'],'dragalge':['Poison','Dragon'],
    'dragapult':['Dragon','Ghost'],'dragonite':['Dragon','Flying'],'drampa':['Normal','Dragon'],
    'drapion':['Poison','Dark'],'drilbur':['Ground'],'druddigon':['Dragon'],
    'dugtrio':['Ground'],'dugtrio-alola':['Ground','Steel'],'duraludon':['Steel','Dragon'],
    'durant':['Bug','Steel'],'dwebble':['Bug','Rock'],
    'eelektross':['Electric'],'eldegoss':['Grass'],'elekid':['Electric'],
    'emboar':['Fire','Fighting'],'empoleon':['Water','Steel'],'entei':['Fire'],
    'escavalier':['Bug','Steel'],'espeon':['Psychic'],'eternatus':['Poison','Dragon'],
    'excadrill':['Ground','Steel'],'exeggutor':['Grass','Psychic'],
    'exeggutor-alola':['Grass','Dragon'],'exploud':['Normal'],
    "farfetchd-galar":['Fighting'],'feraligatr':['Water'],'ferroseed':['Grass','Steel'],
    'ferrothorn':['Grass','Steel'],'floatzel':['Water'],'florges':['Fairy'],
    'flygon':['Ground','Dragon'],'foongus':['Grass','Poison'],'forretress':['Bug','Steel'],
    'frillish':['Water','Ghost'],'froslass':['Ice','Ghost'],'frosmoth':['Ice','Bug'],
    'gallade':['Psychic','Fighting'],'galvantula':['Bug','Electric'],'garbodor':['Poison'],
    'garchomp':['Dragon','Ground'],'gardevoir':['Psychic','Fairy'],'gastly':['Ghost','Poison'],
    'gastrodon':['Water','Ground'],'gengar':['Ghost','Poison'],'gigalith':['Rock'],
    'giratina':['Ghost','Dragon'],'giratina-origin':['Ghost','Dragon'],'glalie':['Ice'],
    'glastrier':['Ice'],'gligar':['Ground','Flying'],'gliscor':['Ground','Flying'],
    'golbat':['Poison','Flying'],'golem':['Rock','Ground'],'golem-alola':['Rock','Electric'],
    'golett':['Ground','Ghost'],'golisopod':['Bug','Water'],'golurk':['Ground','Ghost'],
    'goodra':['Dragon'],'gorebyss':['Water'],'gothitelle':['Psychic'],
    'gourgeist':['Ghost','Grass'],'gourgeist-small':['Ghost','Grass'],
    'gourgeist-super':['Ghost','Grass'],'granbull':['Fairy'],
    'greninja':['Water','Dark'],'greninja-bond':['Water','Dark'],
    'grimer-alola':['Poison','Dark'],'grimmsnarl':['Dark','Fairy'],'grookey':['Grass'],
    'groudon':['Ground'],'gurdurr':['Fighting'],'guzzlord':['Dark','Dragon'],
    'gyarados':['Water','Flying'],
    'hariyama':['Fighting'],'hatterene':['Psychic','Fairy'],'hattrem':['Psychic'],
    'haunter':['Ghost','Poison'],'hawlucha':['Fighting','Flying'],'haxorus':['Dragon'],
    'heatran':['Fire','Steel'],'heliolisk':['Electric','Normal'],'heracross':['Bug','Fighting'],
    'hippopotas':['Ground'],'hippowdon':['Ground'],'hitmonchan':['Fighting'],
    'ho-oh':['Fire','Flying'],'honchkrow':['Dark','Flying'],'hoopa':['Psychic','Ghost'],
    'hoopa-unbound':['Psychic','Dark'],'houndoom':['Dark','Fire'],'houndour':['Dark','Fire'],
    'hydreigon':['Dark','Dragon'],
    'incineroar':['Fire','Dark'],'indeedee':['Psychic','Normal'],'infernape':['Fire','Fighting'],
    'inteleon':['Water'],
    'jellicent':['Water','Ghost'],'jirachi':['Steel','Psychic'],'jolteon':['Electric'],
    'jumpluff':['Grass','Flying'],'jynx':['Ice','Psychic'],
    'kabuto':['Rock','Water'],'kabutops':['Rock','Water'],'kadabra':['Psychic'],
    'kangaskhan':['Normal'],'kartana':['Grass','Steel'],'kecleon':['Normal'],
    'keldeo':['Water','Fighting'],'kingdra':['Water','Dragon'],'klefki':['Steel','Fairy'],
    'klinklang':['Steel'],'koffing':['Poison'],'kommoo':['Dragon','Fighting'],
    'krookodile':['Ground','Dark'],'kyogre':['Water'],'kyurem':['Dragon','Ice'],
    'kyurem-black':['Dragon','Ice'],'kyurem-white':['Dragon','Ice'],
    'landorus':['Ground','Flying'],'landorus-therian':['Ground','Flying'],
    'lanturn':['Water','Electric'],'lapras':['Water','Ice'],'larvesta':['Bug','Fire'],
    'latias':['Dragon','Psychic'],'latios':['Dragon','Psychic'],'leafeon':['Grass'],
    'liepard':['Dark'],'lileep':['Rock','Grass'],'linoone':['Normal'],'lopunny':['Normal'],
    'lucario':['Fighting','Steel'],'ludicolo':['Water','Grass'],'lugia':['Psychic','Flying'],
    'lunala':['Psychic','Ghost'],'lurantis':['Grass'],'lycanroc':['Rock'],
    'lycanroc-dusk':['Rock'],
    'machamp':['Fighting'],'magearna':['Steel','Fairy'],'magmortar':['Fire'],
    'magnemite':['Electric','Steel'],'magneton':['Electric','Steel'],
    'magnezone':['Electric','Steel'],'malamar':['Dark','Psychic'],'mamoswine':['Ice','Ground'],
    'manaphy':['Water'],'mandibuzz':['Dark','Flying'],'manectric':['Electric'],
    'mantine':['Water','Flying'],'mareanie':['Poison','Water'],
    'marowak-alola':['Fire','Ghost'],'marshadow':['Fighting','Ghost'],'mawile':['Steel','Fairy'],
    'medicham':['Fighting','Psychic'],'melmetal':['Steel'],'meloetta':['Normal','Psychic'],
    'meowth':['Normal'],'mesprit':['Psychic'],'metagross':['Steel','Psychic'],
    'mew':['Psychic'],'mewtwo':['Psychic'],'mienfoo':['Fighting'],'mienshao':['Fighting'],
    'milotic':['Water'],'mimikyu':['Ghost','Fairy'],'minccino':['Normal'],
    'minior':['Rock','Flying'],'misdreavus':['Ghost'],'mismagius':['Ghost'],
    'moltres':['Fire','Flying'],'moltres-galar':['Dark','Flying'],
    'morelull':['Grass','Fairy'],'mrmime':['Psychic','Fairy'],
    'mudbray':['Ground'],'mudsdale':['Ground'],'muk-alola':['Poison','Dark'],
    'munchlax':['Normal'],'murkrow':['Dark','Flying'],'musharna':['Psychic'],
    'naganadel':['Poison','Dragon'],'natu':['Psychic','Flying'],'necrozma':['Psychic'],
    'necrozma-dawn-wings':['Psychic','Ghost'],'necrozma-dusk-mane':['Psychic','Steel'],
    'nidoking':['Poison','Ground'],'nidoqueen':['Poison','Ground'],
    'nihilego':['Rock','Poison'],'ninetales':['Fire'],'ninetales-alola':['Ice','Fairy'],
    'ninjask':['Bug','Flying'],'noivern':['Flying','Dragon'],'numel':['Fire','Ground'],
    'omanyte':['Rock','Water'],'omastar':['Rock','Water'],'onix':['Rock','Ground'],
    'oricorio-pom-pom':['Electric','Flying'],'oricorio-sensu':['Ghost','Flying'],
    'palkia':['Water','Dragon'],'palossand':['Ghost','Ground'],'pancham':['Fighting'],
    'pangoro':['Fighting','Dark'],'passimian':['Fighting'],'pawniard':['Dark','Steel'],
    'pelipper':['Water','Flying'],'perrserker':['Steel'],'persian-alola':['Dark'],
    'pidgeot':['Normal','Flying'],'pikipek':['Normal','Flying'],'piloswine':['Ice','Ground'],
    'pinsir':['Bug'],'politoed':['Water'],'poliwrath':['Water','Fighting'],
    'polteageist':['Ghost'],'ponyta':['Fire'],'ponyta-galar':['Psychic'],
    'porygon':['Normal'],'porygon-z':['Normal'],'porygon2':['Normal'],
    'primarina':['Water','Fairy'],'primeape':['Fighting'],'probopass':['Rock','Steel'],
    'pumpkaboo-small':['Ghost','Grass'],'pumpkaboo-super':['Ghost','Grass'],
    'pyukumuku':['Water'],
    'quagsire':['Water','Ground'],'qwilfish':['Water','Poison'],
    'raichu-alola':['Electric','Psychic'],'raikou':['Electric'],
    'raticate-alola':['Dark','Normal'],'rayquaza':['Dragon','Flying'],
    'regice':['Ice'],'regidrago':['Dragon'],'regirock':['Rock'],'registeel':['Steel'],
    'reuniclus':['Psychic'],'rhydon':['Ground','Rock'],'rhyperior':['Ground','Rock'],
    'ribombee':['Bug','Fairy'],'rillaboom':['Grass'],'riolu':['Fighting'],
    'roserade':['Grass','Poison'],'rotom':['Electric','Ghost'],'rotom-frost':['Electric','Ice'],
    'rotom-heat':['Electric','Fire'],'rotom-mow':['Electric','Grass'],
    'rotom-wash':['Electric','Water'],'rufflet':['Normal','Flying'],
    'sableye':['Dark','Ghost'],'salamence':['Dragon','Flying'],'salandit':['Poison','Fire'],
    'salazzle':['Poison','Fire'],'samurott':['Water'],'sandaconda':['Ground'],
    'sandshrew-alola':['Ice','Steel'],'sandslash':['Ground'],'sandslash-alola':['Ice','Steel'],
    'sawk':['Fighting'],'sceptile':['Grass'],'scizor':['Bug','Steel'],
    'scolipede':['Bug','Poison'],'scorbunny':['Fire'],'scrafty':['Dark','Fighting'],
    'scraggy':['Dark','Fighting'],'scyther':['Bug','Flying'],'seismitoad':['Water','Ground'],
    'serperior':['Grass'],'sharpedo':['Water','Dark'],'shaymin':['Grass'],
    'shaymin-sky':['Grass','Flying'],'shedinja':['Bug','Ghost'],'shellder':['Water'],
    'shiftry':['Grass','Dark'],'shuckle':['Bug','Rock'],'sigilyph':['Psychic','Flying'],
    'silvally-dragon':['Dragon'],'silvally-fairy':['Fairy'],'silvally-ghost':['Ghost'],
    'silvally-ground':['Ground'],'silvally-steel':['Steel'],'silvally-water':['Water'],
    'skarmory':['Steel','Flying'],'skrelp':['Poison','Water'],'skuntank':['Poison','Dark'],
    'slowbro':['Water','Psychic'],'slowbro-galar':['Poison','Psychic'],
    'slowking':['Water','Psychic'],'slowking-galar':['Poison','Psychic'],
    'slowpoke':['Water','Psychic'],'slurpuff':['Fairy'],'smeargle':['Normal'],
    'sneasel':['Dark','Ice'],'snivy':['Grass'],'snorlax':['Normal'],'snover':['Grass','Ice'],
    'snubbull':['Fairy'],'spiritomb':['Ghost','Dark'],'spritzee':['Fairy'],
    'stakataka':['Rock','Steel'],'staraptor':['Normal','Flying'],'starmie':['Water','Psychic'],
    'staryu':['Water'],'steelix':['Steel','Ground'],'stoutland':['Normal'],
    'stunky':['Poison','Dark'],'suicune':['Water'],'surskit':['Bug','Water'],
    'swampert':['Water','Ground'],'swanna':['Water','Flying'],'swellow':['Normal','Flying'],
    'sylveon':['Fairy'],
    'taillow':['Normal','Flying'],'talonflame':['Fire','Flying'],'tangela':['Grass'],
    'tangrowth':['Grass'],'tapubulu':['Grass','Fairy'],'tapufini':['Water','Fairy'],
    'tapukoko':['Electric','Fairy'],'tapulele':['Psychic','Fairy'],'tauros':['Normal'],
    'tentacruel':['Water','Poison'],'terrakion':['Rock','Fighting'],'throh':['Fighting'],
    'thundurus':['Electric','Flying'],'thundurus-therian':['Electric','Flying'],
    'timburr':['Fighting'],'tirtouga':['Water','Rock'],'togedemaru':['Electric','Steel'],
    'togekiss':['Fairy','Flying'],'torkoal':['Fire'],'tornadus':['Flying'],
    'tornadus-therian':['Flying'],'torterra':['Grass','Ground'],'toucannon':['Normal','Flying'],
    'toxapex':['Poison','Water'],'toxicroak':['Poison','Fighting'],
    'toxtricity':['Electric','Poison'],'trapinch':['Ground'],'trevenant':['Ghost','Grass'],
    'trubbish':['Poison'],'tsareena':['Grass'],'turtonator':['Fire','Dragon'],
    'typenull':['Normal'],'tyranitar':['Rock','Dark'],'tyrantrum':['Rock','Dragon'],
    'tyrunt':['Rock','Dragon'],
    'umbreon':['Dark'],'ursaring':['Normal'],'urshifu':['Fighting','Dark'],
    'urshifu-rapid-strike':['Fighting','Water'],'uxie':['Psychic'],
    'vanilluxe':['Ice'],'vaporeon':['Water'],'venusaur':['Grass','Poison'],
    'victini':['Psychic','Fire'],'victreebel':['Grass','Poison'],'vigoroth':['Normal'],
    'vikavolt':['Bug','Electric'],'vileplume':['Grass','Poison'],'virizion':['Grass','Fighting'],
    'vivillon':['Bug','Flying'],'volcanion':['Fire','Water'],'volcarona':['Bug','Fire'],
    'vullaby':['Dark','Flying'],'vulpix-alola':['Ice'],
    'walrein':['Ice','Water'],'weavile':['Dark','Ice'],'weezing':['Poison'],
    'weezing-galar':['Poison','Fairy'],'whimsicott':['Grass','Fairy'],
    'wingull':['Water','Flying'],'wishiwashi':['Water'],'wobbuffet':['Psychic'],
    'wynaut':['Psychic'],
    'xatu':['Psychic','Flying'],'xerneas':['Fairy'],'xurkitree':['Electric'],
    'yanmega':['Bug','Flying'],'yveltal':['Dark','Flying'],
    'zamazenta-crowned':['Fighting','Steel'],'zangoose':['Normal'],
    'zapdos':['Electric','Flying'],'zapdos-galar':['Fighting','Flying'],
    'zarude':['Dark','Grass'],'zekrom':['Dragon','Electric'],'zeraora':['Electric'],
    'zigzagoon':['Normal'],'zygarde':['Dragon','Ground'],'zygarde-10%':['Dragon','Ground'],
}

SPRITE_BASE = 'https://play.pokemonshowdown.com/sprites'
TYPE_BASE   = 'https://play.pokemonshowdown.com/sprites/types'
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

SPRITE_ID_EXCEPTIONS = {
    'ho-oh':               'hooh',
    'zygarde-10%':         'zygarde10',
    'necrozma-dusk-mane':  'necrozma-duskmane',
    'necrozma-dawn-wings': 'necrozma-dawnwings',
}

def sprite_id(species):
    s = species.lower().replace(' ','').replace('.','').replace(':','').replace("'",'')
    if s.endswith('-o'):
        s = s[:-2]+'o'
    return SPRITE_ID_EXCEPTIONS.get(s, s)

def item_id(name):
    return re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))

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
        if it.endswith(' Z'):
            parts.append(esc(it))
            continue
        src = ITEM_BASE + '/' + item_id(it) + '.png'
        icon = '<img class="item-icon" src="' + src + '" alt="">'
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

# ── HTML builder ──────────────────────────────────────────────────────────────

def make_html(species, sets, tier):
    sid         = sprite_id(species)
    front_url   = '{}/ani/{}.gif'.format(SPRITE_BASE, sid)
    back_url    = '{}/ani-back/{}.gif'.format(SPRITE_BASE, sid)
    static_url  = '{}/gen5/{}.png'.format(SPRITE_BASE, sid)
    static_back = '{}/gen5-back/{}.png'.format(SPRITE_BASE, sid)

    sprite_tag = (
        '<img class="sprite" id="main-sprite"'
        ' src="{front}"'
        ' data-front="{front}"'
        ' data-back="{back}"'
        ' data-static-front="{static}"'
        ' data-static-back="{staticback}"'
        ' onmouseover="this.src=window.staticMode?this.dataset.staticBack:this.dataset.back"'
        ' onmouseout="this.src=window.staticMode?this.dataset.staticFront:this.dataset.front"'
        ' alt="{name}">'
    ).format(front=front_url, back=back_url, static=static_url, staticback=static_back, name=esc(species))

    toggle_btn = (
        '<button class="sprite-toggle" onclick="'
        'var img=document.getElementById(\'main-sprite\');'
        'window.staticMode=!window.staticMode;'
        'img.src=window.staticMode?img.dataset.staticFront:img.dataset.front;'
        'this.textContent=window.staticMode?\'GIF\':\'PNG\''
        '">PNG</button>'
    )

    cards = ''
    for s in sets:
        level     = s.get('level')
        moves     = s.get('moves', [])
        ivs       = s.get('ivs')
        happiness = s.get('happiness')

        # Moves column — always exactly 4 rows
        move_rows = ''.join(
            row('Move {}'.format(i+1), esc(fmt_list(slot)))
            for i, slot in enumerate(moves)
        )

        # Stats column
        iv_str    = fmt_ivs(ivs)
        stat_rows = (
            '<div class="row"><span class="row-label">Item</span>'
            '<span class="row-value">{}</span></div>'.format(item_html(s.get('item',[]))) +
            row('Ability', esc(fmt_list(s.get('ability',[])))) +
            row('Nature',  esc(fmt_nature(s.get('nature','')))) +
            row('EVs',     esc(fmt_evs(s.get('evs',{}), happiness)))
        )

        # Extra row — level and/or IVs when present
        extra_tags = []
        if level:
            extra_tags.append('Lv {}'.format(level))
        if iv_str:
            extra_tags.append('IVs: {}'.format(iv_str))
        extra_html = ''
        if extra_tags:
            chips = ''.join('<span class="extra-chip">{}</span>'.format(t) for t in extra_tags)
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
        '  <title>{} \u2014 Gen 7 Battle Factory</title>'.format(esc(species)),
        '  <link rel="stylesheet" href="../../../../styles.css">',
        '</head>',
        '<body class="g7bf">',
        '  <a class="back-link" href="../">\u2190 {}</a>'.format(esc(tier)),
        '  <div class="page-header">',
        '    {}'.format(sprite_tag),
        '    <div class="name-block">',
        '      <h1>{}</h1>'.format(esc(species)),
        '      {}'.format(type_badges_html(sid)),
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

    script_dir = os.path.dirname(os.path.abspath(__file__))
    css_src    = os.path.join(script_dir, 'styles.css')
    css_dst    = os.path.join(output_dir, 'styles.css')
    if os.path.exists(css_src) and os.path.abspath(css_src) != os.path.abspath(css_dst):
        shutil.copy(css_src, css_dst)
        print('Copied styles.css \u2192', css_dst)
    else:
        print('WARNING: styles.css not found \u2014 skipped.')

    print('Generated {} files across {} tier(s): {}'.format(
        total, len(tiers), ', '.join(tiers)))

if __name__ == '__main__':
    main()
