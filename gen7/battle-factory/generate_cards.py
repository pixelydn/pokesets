"""
Generates mon-card HTML snippets for a tier index page.
Prints to stdout — pipe or paste into your mon-grid div.

Usage:
    python generate_cards.py <factory-sets.json> <tier>

Examples:
    python generate_cards.py factory-sets.json OU
    python generate_cards.py factory-sets.json Uber
"""

import json, sys, re

SPRITE = 'https://play.pokemonshowdown.com/sprites'

TYPES = {
    'abomasnow':['Grass','Ice'],'abra':['Psychic'],'absol':['Dark'],
    'accelgor':['Bug'],'aegislash':['Steel','Ghost'],'aerodactyl':['Rock','Flying'],
    'aggron':['Steel','Rock'],'alakazam':['Psychic'],'alomomola':['Water'],
    'amaura': ['Rock', 'Ice'],
    'altaria':['Dragon','Flying'],'ambipom':['Normal'],'amoonguss':['Grass','Poison'],
    'ampharos':['Electric'],'anorith':['Rock','Bug'],'araquanid':['Water','Bug'],
    'arcanine':['Fire'],'arceus':['Normal'],'arceus-dark':['Dark'],
    'arceus-dragon':['Dragon'],'arceus-electric':['Electric'],'arceus-fairy':['Fairy'],
    'arceus-flying':['Flying'],'arceus-ghost':['Ghost'],'arceus-grass':['Grass'],
    'arceus-ground':['Ground'],'arceus-poison':['Poison'],'arceus-rock':['Rock'],
    'arceus-steel':['Steel'],'arceus-water':['Water'],
    'archen':['Rock','Flying'],'archeops':['Rock','Flying'],'arctovish':['Water','Ice'],
    'armarouge':['Fire','Psychic'],'armaldo':['Rock','Bug'],'aromatisse':['Fairy'],
    'articuno':['Ice','Flying'],'articuno-galar':['Psychic','Flying'],
    'audino':['Normal'],'aurorus':['Rock','Ice'],'avalugg':['Ice'],
    'azelf':['Psychic'],'azumarill':['Water','Fairy'],
    'barbaracle':['Rock','Water'],'basculegion':['Water','Ghost'],
    'basculegion-f':['Water','Ghost'],'beartic':['Ice'],'beedrill':['Bug','Poison'],
    'bellossom':['Grass'],'bellibolt':['Electric'],'bewear':['Normal','Fighting'],
    'bisharp':['Dark','Steel'],'blacephalon':['Fire','Ghost'],'blastoise':['Water'],
    'blaziken':['Fire','Fighting'],'blissey':['Normal'],'bombirdier':['Flying','Dark'],
    'brambleghast':['Grass','Ghost'],'braviary':['Normal','Flying'],
    'braviary-hisui':['Psychic','Flying'],'breloom':['Grass','Fighting'],
    'bronzong':['Steel','Psychic'],'bruxish':['Water','Psychic'],
    'bulbasaur': ['Grass', 'Poison'],
    'buneary': ['Normal'],
    'bunnelby': ['Normal'],
    'buzzwole':['Bug','Fighting'],
    'cacturne':['Grass','Dark'],'calyrex-ice':['Psychic','Ice'],
    'calyrex-shadow':['Psychic','Ghost'],'camerupt':['Fire','Ground'],
    'carracosta':['Water','Rock'],'carvanha':['Water','Dark'],'celebi':['Psychic','Grass'],
    'celesteela':['Steel','Flying'],'centiskorch':['Fire','Bug'],
    'chandelure':['Ghost','Fire'],'chansey':['Normal'],'charizard':['Fire','Flying'],
    'chesnaught':['Grass','Fighting'],'chien-pao':['Dark','Ice'],
    'chinchou':['Water','Electric'],'cinccino':['Normal'],'cinderace':['Fire'],
    'clamperl':['Water'],'clefable':['Fairy'],'clefairy':['Fairy'],
    'clodsire':['Poison','Ground'],'cloyster':['Water','Ice'],
    'coalossal':['Rock','Fire'],'cobalion':['Steel','Fighting'],'cofagrigus':['Ghost'],
    'combusken':['Fire','Fighting'],'comfey':['Fairy'],'conkeldurr':['Fighting'],
    'copperajah':['Steel'],'corphish':['Water'],'corviknight':['Flying','Steel'],
    'cottonee':['Grass','Fairy'],'crabominable':['Fighting','Ice'],'cradily':['Rock','Grass'],
    'cramorant':['Flying','Water'],'crawdaunt':['Water','Dark'],'cresselia':['Psychic'],
    'croagunk':['Poison','Fighting'],'crobat':['Poison','Flying'],'cryogonal':['Ice'],
    'cyclizar':['Dragon','Normal'],
    'darkrai':['Dark'],'darmanitan':['Fire'],'darmanitan-galar':['Ice'],
    'decidueye':['Grass','Ghost'],'decidueye-hisui':['Grass','Fighting'],
    'delphox':['Fire','Psychic'],'deoxys-attack':['Psychic'],
    'deoxys-defense':['Psychic'],'deoxys-speed':['Psychic'],'dhelmise':['Ghost','Grass'],
    'dialga':['Steel','Dragon'],'diancie':['Rock','Fairy'],'diggersby':['Normal','Ground'],
    'diglett':['Ground'],'ditto':['Normal'],'doduo':['Normal','Flying'],
    'dondozo':['Water'],'donphan':['Ground'],'doublade':['Steel','Ghost'],
    'dragalge':['Poison','Dragon'],'dragapult':['Dragon','Ghost'],
    'dragonite':['Dragon','Flying'],'drampa':['Normal','Dragon'],'drapion':['Poison','Dark'],
    'drilbur':['Ground'],'druddigon':['Dragon'],'dudunsparce':['Normal'],
    'dugtrio':['Ground'],'dugtrio-alola':['Ground','Steel'],
    'duraludon':['Steel','Dragon'],'durant':['Bug','Steel'],'dwebble':['Bug','Rock'],
    'eelektross':['Electric'],'eldegoss':['Grass'],'elekid':['Electric'],
    'electrode-hisui':['Electric','Grass'],'emboar':['Fire','Fighting'],
    'empoleon':['Water','Steel'],'enamorus':['Fairy','Flying'],
    'enamorus-therian':['Fairy','Flying'],'entei':['Fire'],'escavalier':['Bug','Steel'],
    'espeon':['Psychic'],'eternatus':['Poison','Dragon'],'excadrill':['Ground','Steel'],
    'exeggutor':['Grass','Psychic'],'exeggutor-alola':['Grass','Dragon'],'exploud':['Normal'],
    'farfetchd-galar':['Fighting'],'feraligatr':['Water'],'ferroseed':['Grass','Steel'],
    'ferrothorn':['Grass','Steel'],'fezandipiti':['Poison','Fairy'],
    'floatzel':['Water'],'florges':['Fairy'],'fluttermane':['Ghost','Fairy'],
    'flygon':['Ground','Dragon'],'foongus':['Grass','Poison'],'forretress':['Bug','Steel'],
    'frillish':['Water','Ghost'],'froslass':['Ice','Ghost'],'frosmoth':['Ice','Bug'],
    'gallade':['Psychic','Fighting'],'galvantula':['Bug','Electric'],'garbodor':['Poison'],
    'garchomp':['Dragon','Ground'],'gardevoir':['Psychic','Fairy'],'garganacl':['Rock'],
    'gastly':['Ghost','Poison'],'gastrodon':['Water','Ground'],'gengar':['Ghost','Poison'],
    'gholdengo':['Steel','Ghost'],'gigalith':['Rock'],'giratina':['Ghost','Dragon'],
    'giratina-origin':['Ghost','Dragon'],'glalie':['Ice'],'glastrier':['Ice'],
    'gligar':['Ground','Flying'],'glimmora':['Rock','Poison'],'gliscor':['Ground','Flying'],
    'golbat':['Poison','Flying'],'golem':['Rock','Ground'],'golem-alola':['Rock','Electric'],
    'golett':['Ground','Ghost'],'golisopod':['Bug','Water'],'golurk':['Ground','Ghost'],
    'goodra':['Dragon'],'goodra-hisui':['Steel','Dragon'],'gorebyss':['Water'],
    'gothitelle':['Psychic'],'gourgeist':['Ghost','Grass'],'gourgeist-small':['Ghost','Grass'],
    'gourgeist-super':['Ghost','Grass'],'granbull':['Fairy'],
    'greattusk':['Ground','Fighting'],'greninja':['Water','Dark'],
    'greninja-bond':['Water','Dark'],'grimmsnarl':['Dark','Fairy'],'groudon':['Ground'],
    'grimer-alola': ['Poison', 'Dark'],
    'gurdurr':['Fighting'],'guzzlord':['Dark','Dragon'],'gyarados':['Water','Flying'],
    'hariyama':['Fighting'],'hatterene':['Psychic','Fairy'],'hattrem':['Psychic'],
    'haunter':['Ghost','Poison'],'hawlucha':['Fighting','Flying'],'haxorus':['Dragon'],
    'heatran':['Fire','Steel'],'heliolisk':['Electric','Normal'],'heracross':['Bug','Fighting'],
    'hippopotas':['Ground'],'hippowdon':['Ground'],'hitmonchan':['Fighting'],
    'ho-oh':['Fire','Flying'],'honchkrow':['Dark','Flying'],'hoopa':['Psychic','Ghost'],
    'hoopa-unbound':['Psychic','Dark'],'houndoom':['Dark','Fire'],'houndour':['Dark','Fire'],
    'hydrapple':['Grass','Dragon'],'hydreigon':['Dark','Dragon'],
    'incineroar':['Fire','Dark'],'indeedee':['Psychic','Normal'],'infernape':['Fire','Fighting'],
    'inteleon':['Water'],'ironbundle':['Ice','Water'],'ironcrown':['Steel','Psychic'],
    'ironmoth':['Fire','Poison'],'ironvaliant':['Fairy','Fighting'],
    'jellicent':['Water','Ghost'],'jirachi':['Steel','Psychic'],'jolteon':['Electric'],
    'jumpluff':['Grass','Flying'],'jynx':['Ice','Psychic'],
    'kabuto':['Rock','Water'],'kabutops':['Rock','Water'],'kadabra':['Psychic'],
    'kangaskhan':['Normal'],'kartana':['Grass','Steel'],'kecleon':['Normal'],
    'keldeo':['Water','Fighting'],'kilowattrel':['Electric','Flying'],
    'kingambit':['Dark','Steel'],'kingdra':['Water','Dragon'],'kleavor':['Bug','Rock'],
    'klefki':['Steel','Fairy'],'klinklang':['Steel'],'koffing':['Poison'],
    'kommoo':['Dragon','Fighting'],'koraidon':['Fighting','Dragon'],
    'krookodile':['Ground','Dark'],'kyogre':['Water'],'kyurem':['Dragon','Ice'],
    'kyurem-black':['Dragon','Ice'],'kyurem-white':['Dragon','Ice'],
    'landorus':['Ground','Flying'],'landorus-therian':['Ground','Flying'],
    'lanturn':['Water','Electric'],'lapras':['Water','Ice'],'larvesta':['Bug','Fire'],
    'latias':['Dragon','Psychic'],'latios':['Dragon','Psychic'],'leafeon':['Grass'],
    'liepard':['Dark'],'lileep':['Rock','Grass'],'linoone':['Normal'],
    'lilligant-hisui':['Grass','Fighting'],'lokix':['Bug','Dark'],'lopunny':['Normal'],
    'lucario':['Fighting','Steel'],'ludicolo':['Water','Grass'],'lugia':['Psychic','Flying'],
    'lunala':['Psychic','Ghost'],'lurantis':['Grass'],'lycanroc':['Rock'],
    'lycanroc-dusk':['Rock'],
    'machamp':['Fighting'],'magearna':['Steel','Fairy'],'magmortar':['Fire'],
    'magnemite':['Electric','Steel'],'magneton':['Electric','Steel'],
    'magnezone':['Electric','Steel'],'malamar':['Dark','Psychic'],'mamoswine':['Ice','Ground'],
    'manaphy':['Water'],'mandibuzz':['Dark','Flying'],'manectric':['Electric'],
    'mantine':['Water','Flying'],'mareanie':['Poison','Water'],
    'marowak-alola':['Fire','Ghost'],'marshadow':['Fighting','Ghost'],
    'maushold':['Normal'],'mawile':['Steel','Fairy'],'medicham':['Fighting','Psychic'],
    'melmetal':['Steel'],'meloetta':['Normal','Psychic'],'meowscarada':['Grass','Dark'],
    'meowth':['Normal'],'mesprit':['Psychic'],'metagross':['Steel','Psychic'],
    'mew':['Psychic'],'mewtwo':['Psychic'],'mienfoo':['Fighting'],'mienshao':['Fighting'],
    'milotic':['Water'],'mimikyu':['Ghost','Fairy'],'minccino':['Normal'],
    'minior':['Rock','Flying'],'misdreavus':['Ghost'],'mismagius':['Ghost'],
    'moltres':['Fire','Flying'],'moltres-galar':['Dark','Flying'],
    'morelull':['Grass','Fairy'],'mrmime':['Psychic','Fairy'],
    'mudbray':['Ground'],'mudsdale':['Ground'],'muk-alola':['Poison','Dark'],
    'munchlax':['Normal'],'munkidori':['Poison','Psychic'],'murkrow':['Dark','Flying'],
    'musharna':['Psychic'],
    'naclstack':['Rock'],'naganadel':['Poison','Dragon'],'natu':['Psychic','Flying'],
    'necrozma':['Psychic'],'necrozma-dawn-wings':['Psychic','Ghost'],
    'necrozma-dusk-mane':['Psychic','Steel'],'nidoking':['Poison','Ground'],
    'nidoqueen':['Poison','Ground'],'nihilego':['Rock','Poison'],'ninetales':['Fire'],
    'ninetales-alola':['Ice','Fairy'],'ninjask':['Bug','Flying'],'noivern':['Flying','Dragon'],
    'numel':['Fire','Ground'],
    'ogerpon':['Grass'],'ogerpon-cornerstone':['Grass','Rock'],
    'ogerpon-wellspring':['Grass','Water'],'okidogi':['Poison','Fighting'],
    'omanyte':['Rock','Water'],'omastar':['Rock','Water'],'onix':['Rock','Ground'],
    'oricorio':['Fire','Flying'],'oricorio-pom-pom':['Electric','Flying'],
    'oricorio-sensu':['Ghost','Flying'],'orthworm':['Steel'],'overqwil':['Dark','Poison'],
    'palkia':['Water','Dragon'],'palossand':['Ghost','Ground'],'pancham':['Fighting'],
    'pangoro':['Fighting','Dark'],'passimian':['Fighting'],'pawmot':['Electric','Fighting'],
    'pawniard':['Dark','Steel'],'pecharunt':['Poison','Ghost'],'pelipper':['Water','Flying'],
    'perrserker':['Steel'],'persian-alola':['Dark'],'pidgeot':['Normal','Flying'],
    'pikipek':['Normal','Flying'],'piloswine':['Ice','Ground'],'pinsir':['Bug'],
    'politoed':['Water'],'poliwrath':['Water','Fighting'],'polteageist':['Ghost'],
    'ponyta':['Fire'],'ponyta-galar':['Psychic'],'porygon':['Normal'],
    'porygon-z':['Normal'],'porygon2':['Normal'],'primarina':['Water','Fairy'],
    'primeape':['Fighting'],'probopass':['Rock','Steel'],
    'pumpkaboo-small':['Ghost','Grass'],'pumpkaboo-super':['Ghost','Grass'],
    'pyukumuku':['Water'],
    'quagsire':['Water','Ground'],'quaquaval':['Water','Fighting'],
    'qwilfish':['Water','Poison'],'qwilfish-hisui':['Dark','Poison'],
    'ragingbolt':['Electric','Dragon'],'raichu-alola':['Electric','Psychic'],
    'raikou':['Electric'],'raticate-alola':['Dark','Normal'],'rayquaza':['Dragon','Flying'],
    'regice':['Ice'],'regidrago':['Dragon'],'regirock':['Rock'],'registeel':['Steel'],
    'reuniclus':['Psychic'],'revavroom':['Steel','Poison'],'rhydon':['Ground','Rock'],
    'rhyperior':['Ground','Rock'],'ribombee':['Bug','Fairy'],'rillaboom':['Grass'],
    'riolu':['Fighting'],'roaringmoon':['Dragon','Dark'],'roserade':['Grass','Poison'],
    'rotom':['Electric','Ghost'],'rotom-frost':['Electric','Ice'],
    'rotom-heat':['Electric','Fire'],'rotom-mow':['Electric','Grass'],
    'rotom-wash':['Electric','Water'],'rufflet':['Normal','Flying'],
    'sableye':['Dark','Ghost'],'salamence':['Dragon','Flying'],'salandit':['Poison','Fire'],
    'salazzle':['Poison','Fire'],'samurott':['Water'],'samurott-hisui':['Water','Dark'],
    'sandaconda':['Ground'],'sandshrew-alola':['Ice','Steel'],'sandslash':['Ground'],
    'sandslash-alola':['Ice','Steel'],'sandyshocks':['Electric','Ground'],'sawk':['Fighting'],
    'sceptile':['Grass'],'scizor':['Bug','Steel'],'scolipede':['Bug','Poison'],
    'scorbunny':['Fire'],'scrafty':['Dark','Fighting'],'scraggy':['Dark','Fighting'],
    'screamtail':['Fairy','Psychic'],'scyther':['Bug','Flying'],
    'seismitoad':['Water','Ground'],'serperior':['Grass'],'sharpedo':['Water','Dark'],
    'shaymin':['Grass'],'shaymin-sky':['Grass','Flying'],'shedinja':['Bug','Ghost'],
    'shellder':['Water'],'shiftry':['Grass','Dark'],'shuckle':['Bug','Rock'],
    'sigilyph':['Psychic','Flying'],'silvally-dragon':['Dragon'],'silvally-fairy':['Fairy'],
    'silvally-ghost':['Ghost'],'silvally-ground':['Ground'],'silvally-steel':['Steel'],
    'silvally-water':['Water'],'sinistcha':['Grass','Ghost'],'skarmory':['Steel','Flying'],
    'skeledirge':['Fire','Ghost'],'skrelp':['Poison','Water'],'skuntank':['Poison','Dark'],
    'slitherwing':['Bug','Fighting'],'slowbro':['Water','Psychic'],
    'slowbro-galar':['Poison','Psychic'],'slowking':['Water','Psychic'],
    'slowking-galar':['Poison','Psychic'],'slowpoke':['Water','Psychic'],
    'slurpuff':['Fairy'],'smeargle':['Normal'],'sneasel':['Dark','Ice'],
    'sneasel-hisui':['Fighting','Poison'],'snivy':['Grass'],'snorlax':['Normal'],
    'snover':['Grass','Ice'],'snubbull':['Fairy'],'spiritomb':['Ghost','Dark'],
    'spritzee':['Fairy'],'stakataka':['Rock','Steel'],'staraptor':['Normal','Flying'],
    'starmie':['Water','Psychic'],'staryu':['Water'],'steelix':['Steel','Ground'],
    'stoutland':['Normal'],'stunky':['Poison','Dark'],'suicune':['Water'],
    'surskit':['Bug','Water'],'swampert':['Water','Ground'],'swanna':['Water','Flying'],
    'swellow':['Normal','Flying'],'sylveon':['Fairy'],
    'taillow':['Normal','Flying'],'talonflame':['Fire','Flying'],'tangela':['Grass'],
    'tangrowth':['Grass'],'tapubulu':['Grass','Fairy'],'tapufini':['Water','Fairy'],
    'tapukoko':['Electric','Fairy'],'tapulele':['Psychic','Fairy'],
    'tatsugiri':['Dragon','Water'],'tauros':['Normal'],
    'tauros-paldea-aqua':['Fighting','Water'],'tauros-paldea-blaze':['Fighting','Fire'],
    'tentacruel':['Water','Poison'],'terrakion':['Rock','Fighting'],'throh':['Fighting'],
    'thundurus':['Electric','Flying'],'thundurus-therian':['Electric','Flying'],
    'timburr':['Fighting'],'ting-lu':['Dark','Ground'],'tinglu':['Dark','Ground'],
    'tinkaton':['Fairy','Steel'],'tirtouga':['Water','Rock'],'togedemaru':['Electric','Steel'],
    'togekiss':['Fairy','Flying'],'torkoal':['Fire'],'tornadus':['Flying'],
    'tornadus-therian':['Flying'],'torterra':['Grass','Ground'],'toucannon':['Normal','Flying'],
    'toxapex':['Poison','Water'],'toxicroak':['Poison','Fighting'],
    'toxtricity':['Electric','Poison'],'trapinch':['Ground'],'trevenant':['Ghost','Grass'],
    'trubbish':['Poison'],'tsareena':['Grass'],'turtonator':['Fire','Dragon'],
    'typhlosion-hisui':['Fire','Ghost'],'typenull':['Normal'],'tyranitar':['Rock','Dark'],
    'tyrantrum':['Rock','Dragon'],'tyrunt':['Rock','Dragon'],
    'umbreon':['Dark'],'ursaluna':['Ground','Normal'],'ursaring':['Normal'],
    'urshifu':['Fighting','Dark'],'urshifu-rapid-strike':['Fighting','Water'],'uxie':['Psychic'],
    'vanilluxe':['Ice'],'vaporeon':['Water'],'venusaur':['Grass','Poison'],
    'victini':['Psychic','Fire'],'victreebel':['Grass','Poison'],'vigoroth':['Normal'],
    'vikavolt':['Bug','Electric'],'vileplume':['Grass','Poison'],'virizion':['Grass','Fighting'],
    'vivillon':['Bug','Flying'],'volcanion':['Fire','Water'],'volcarona':['Bug','Fire'],
    'vullaby':['Dark','Flying'],'vulpix-alola':['Ice'],
    'walrein':['Ice','Water'],'weavile':['Dark','Ice'],'weezing':['Poison'],
    'weezing-galar':['Poison','Fairy'],'whimsicott':['Grass','Fairy'],
    'wingull':['Water','Flying'],'wishiwashi':['Water'],'wobbuffet':['Psychic'],
    'wo-chien':['Dark','Grass'],'wynaut':['Psychic'],
    'xatu':['Psychic','Flying'],'xerneas':['Fairy'],'xurkitree':['Electric'],
    'yanmega':['Bug','Flying'],'yveltal':['Dark','Flying'],
    'zacian':['Fairy'],'zamazenta':['Fighting'],'zamazenta-crowned':['Fighting','Steel'],
    'zangoose':['Normal'],'zapdos':['Electric','Flying'],'zapdos-galar':['Fighting','Flying'],
    'zarude':['Dark','Grass'],'zekrom':['Dragon','Electric'],'zeraora':['Electric'],
    'zigzagoon':['Normal'],'zoroark':['Dark'],'zoroark-hisui':['Normal','Ghost'],
    'zygarde':['Dragon','Ground'],'zygarde-10%':['Dragon','Ground'],
}

SPRITE_ID_EXCEPTIONS = {'porygon-z': 'porygonz'}

def sprite_id(species):
    s = species.lower().replace(' ','').replace('.','').replace(':','').replace("'",'')
    if s.endswith('-o'):
        s = s[:-2] + 'o'
    return SPRITE_ID_EXCEPTIONS.get(s, s)

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    tier      = sys.argv[2]

    data = json.loads(open(json_path, encoding='utf-8').read())

    if tier not in data:
        print('Tier not found. Available:', list(data.keys()))
        sys.exit(1)

    mons = sorted(
        [(slug, mon['sets'][0]['species']) for slug, mon in data[tier].items()],
        key=lambda x: x[1]
    )

    for slug, species in mons:
        sid   = sprite_id(species)
        front  = SPRITE + '/gen5ani/' + sid + '.gif'
        back   = SPRITE + '/gen5ani-back/' + sid + '.gif'
        name  = species.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        badges = ''.join(
            '<span class="type-badge type-{t}">{T}</span>'.format(t=t.lower(), T=t.upper())
            for t in TYPES.get(sid, [])
        )

        print(
            '<a class="mon-card" href="{slug}/" data-name="{name}">\n'
            '  <img class="mon-sprite"\n'
            '    src="{front}"\n'
            '    data-front="{front}"\n'
            '    data-back="{back}"\n'
            '    onmouseover="this.src=this.dataset.back"\n'
            '    onmouseout="this.src=this.dataset.front"\n'
            '\n'
            '    alt="{name}">\n'
            '  <div class="mon-info">\n'
            '    <span class="mon-name">{name}</span>\n'
            '    <div class="mon-types">{badges}</div>\n'
            '  </div>\n'
            '</a>'.format(slug=slug, name=name, front=front, back=back, badges=badges)
        )


if __name__ == '__main__':
    main()
