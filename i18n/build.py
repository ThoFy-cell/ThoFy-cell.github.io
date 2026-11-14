#!/usr/bin/env python3
"""Génère en/index.html et de/index.html à partir de index.html (français, seule source à modifier).
Usage : python3 i18n/build.py   (depuis la racine du dépôt)
Les textes sont traduits via i18n/en.json et i18n/de.json (clé = texte français exact du bloc).
Un texte français sans traduction reste en français et est listé à la fin : ajouter sa traduction aux deux fichiers JSON."""
import re, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
a = src.index('<body'); b = src.index('<script>', a)
head, body, tail = src[:a], src[a:b], src[b:]
INLINE = {'b','a','i','em','strong','code','br','small','u','span','kbd','sup','sub'}
segs, out, cur = [], [], []
def flush():
    global cur
    if not cur: return
    txt = ''.join(cur); cur = []
    if re.search(r'[A-Za-zÀ-ÿ]', re.sub(r'<[^>]+>', '', txt)):
        lead = re.match(r'\s*', txt).group(0); trail = re.search(r'\s*$', txt).group(0)
        segs.append(txt[len(lead):len(txt) - len(trail)]); out.append((lead, len(segs) - 1, trail))
    else: out.append(txt)
for t in re.split(r'(<[^>]+>)', body):
    if t.startswith('<'):
        m = re.match(r'</?\s*([a-zA-Z0-9]+)', t)
        if m and m.group(1).lower() in INLINE: cur.append(t)
        else: flush(); out.append(t)
    else: cur.append(t)
flush()
def strip_attrs(s):
    """<a href=…> → <a#0> : la traduction garde les balises à attributs sous forme de jetons numérotés."""
    found = []
    def r(m): found.append(m.group(0)); return '<%s#%d>' % (m.group(1), len(found) - 1)
    return re.sub(r'<(a|span|small|i|em|code)\s[^>]*>', r, s), found
def norm(s):  # compatibilité avec les clés d'origine (<a46_0>) : on numérote dans l'ordre
    n = [0]
    def r(m): k = '<%s#%d>' % (m.group(1), n[0]); n[0] += 1; return k
    return re.sub(r'<(a|span|small|i|em|code)\d+_\d+>', r, s)

JS = [  # (fragment exact du script français, anglais, allemand)
 ("x.toLocaleString('fr-FR')", "x.toLocaleString('en-GB')", "x.toLocaleString('de-DE')"),
 ("toLocaleDateString('fr-FR'", "toLocaleDateString('en-GB'", "toLocaleDateString('de-DE'"),
 ("label: 'Astuces'", "label: 'Tips'", "label: 'Tipps'"),
 ("label: 'Cargo'", "label: 'Cargo'", "label: 'Frachtschiff'"),
 ("label: 'Participation', note: 'Sièges de la semaine, aide, dons et éliminations.'", "label: 'Participation', note: 'Sieges of the week, help, donations and kills.'", "label: 'Beteiligung', note: 'Belagerungen der Woche, Hilfe, Spenden und Kills.'"),
 ("`Sièges ${v(r.s)} · Aide ${v(r.a)}e · Dons ${v(r.d)}e · Élim. ${v(r.e)}e`", "`Sieges ${v(r.s)} · Help #${v(r.a)} · Donations #${v(r.d)} · Kills #${v(r.e)}`", "`Belagerungen ${v(r.s)} · Hilfe ${v(r.a)}. · Spenden ${v(r.d)}. · Kills ${v(r.e)}.`"),
 ("label: 'Puissance', note: 'Puissance relevée dans la liste des membres.'", "label: 'Power', note: 'Power read from the member list.'", "label: 'Stärke', note: 'Stärke aus der Mitgliederliste.'"),
 ("`${v(r.p)} M de puissance`", "`${v(r.p)}M power`", "`${v(r.p)} Mio. Stärke`"),
 ("label: 'Combiné', note: '70 % participation + 30 % puissance.'", "label: 'Combined', note: '70% participation + 30% power.'", "label: 'Kombiniert', note: '70 % Beteiligung + 30 % Stärke.'"),
 ("`Participation ${r.part} · Puissance ${r.puis}`", "`Participation ${r.part} · Power ${r.puis}`", "`Beteiligung ${r.part} · Stärke ${r.puis}`"),
 ("label: 'Coffres'", "label: 'Chests'", "label: 'Truhen'"),
 ("label: 'Règles'", "label: 'Rules'", "label: 'Regeln'"),
 ("`Relevé du ${DATA.date} · ${rows.length} membres`", "`Data from ${DATA.date} · ${rows.length} members`", "`Stand vom ${DATA.date} · ${rows.length} Mitglieder`"),
 ("`Avec ${stock} coffres : ${gagnants} membres récompensés. « 1er dès 12 » = 1er coffre si la ville en a au moins 12.`", "`With ${stock} chests: ${gagnants} members rewarded. \"1st from 12\" = 1st chest if the city has at least 12.`", "`Mit ${stock} Truhen: ${gagnants} Mitglieder belohnt. „1. ab 12“ = 1. Truhe, wenn die Stadt mindestens 12 hat.`"),
 ("`1er dès ${r.seuils[0]} · 2e dès ${r.seuils[1]} · 3e dès ${r.seuils[2]}`", "`1st from ${r.seuils[0]} · 2nd from ${r.seuils[1]} · 3rd from ${r.seuils[2]}`", "`1. ab ${r.seuils[0]} · 2. ab ${r.seuils[1]} · 3. ab ${r.seuils[2]}`"),
 ("'coffre' + (nb(r) > 1 ? 's' : '')", "'chest' + (nb(r) > 1 ? 's' : '')", "'Truhe' + (nb(r) > 1 ? 'n' : '')"),
 ("'Aucun membre ne correspond.'", "'No member matches.'", "'Kein Mitglied passt.'"),
 ("['😴 Dimanche : repos', \"Pas de duel aujourd'hui. Ne dépense rien d'important, lance tes longs chantiers et prépare lundi.\"]", "['😴 Sunday: rest', \"No duel today. Don't spend anything important, start your long builds and prepare Monday.\"]", "['😴 Sonntag: Ruhetag', \"Heute kein Duell. Gib nichts Wichtiges aus, starte lange Bauten und bereite Montag vor.\"]"),
 ("['🦅 Lundi : Intel, griffon et récolte', \"Dépense ton endurance, fais tes tâches d'Intel, utilise tes noyaux de bête et envoie récolter. Garde tout le reste.\"]", "['🦅 Monday: Intel, griffin and gathering', \"Spend your stamina, do your Intel Tasks, use your Beast Cores and send gatherers. Keep everything else.\"]", "['🦅 Montag: Intel, Greif und Sammeln', \"Gib deine Ausdauer aus, erledige Intel-Aufgaben, nutze Bestienkerne und schick Sammler los. Heb alles andere auf.\"]"),
 ("['🏰 Mardi : château', \"Accélérateurs de construction, wagons et primes UR, tickets d'ouvriers. Termine tes bâtiments aujourd'hui.\"]", "['🏰 Tuesday: castle', \"Construction speed-ups, UR wagons and bounties, worker tickets. Finish your buildings today.\"]", "['🏰 Dienstag: Schloss', \"Baubeschleuniger, UR-Wagen und -Kopfgelder, Arbeitertickets. Schließe deine Gebäude heute ab.\"]"),
 ("['🔬 Mercredi : recherche', \"Accélérateurs de recherche, médailles d'honneur, tâches d'Intel. Termine tes recherches aujourd'hui.\"]", "['🔬 Wednesday: research', \"Research speed-ups, Honor Medals, Intel Tasks. Finish your research today.\"]", "['🔬 Mittwoch: Forschung', \"Forschungsbeschleuniger, Ehrenmedaillen, Intel-Aufgaben. Schließe deine Forschungen heute ab.\"]"),
 ("['🦸 Jeudi : héros', \"C'est le jour des tickets de recrutement, des fragments de héros et des médailles de compétence.\"]", "['🦸 Thursday: heroes', \"The day for recruitment tickets, hero shards and Skill Medals.\"]", "['🦸 Donnerstag: Helden', \"Der Tag für Rekrutierungstickets, Heldenfragmente und Fertigkeitsmedaillen.\"]"),
 ("['🛡️ Vendredi : soldats', \"Entraîne des soldats du plus haut niveau, utilise accélérateurs d'entraînement, wagons et primes UR.\"]", "['🛡️ Friday: soldiers', \"Train top-level soldiers, use training speed-ups, UR wagons and bounties.\"]", "['🛡️ Freitag: Soldaten', \"Trainiere Soldaten der höchsten Stufe, nutze Trainingsbeschleuniger, UR-Wagen und -Kopfgelder.\"]"),
 ("['⚔️ Samedi : combat', \"Journée qui vaut double. Tous les accélérateurs comptent. Suis les consignes des R4 et du R5, bouclier si tu t'absentes.\"]", "['⚔️ Saturday: combat', \"This day counts double. All speed-ups count. Follow the R4s' and R5's instructions, shield up if you are away.\"]", "['⚔️ Samstag: Kampf', \"Der Tag zählt doppelt. Alle Beschleuniger zählen. Folge den Anweisungen der R4 und des R5, Schild, wenn du weg bist.\"]"),
 ("{G: ['Griffon', 1], C: ['Château', 2], R: ['Recherche', 3], H: ['Héros', 4], S: ['Soldats', 5]}", "{G: ['Griffin', 1], C: ['Castle', 2], R: ['Research', 3], H: ['Heroes', 4], S: ['Soldiers', 5]}", "{G: ['Greif', 1], C: ['Schloss', 2], R: ['Forschung', 3], H: ['Helden', 4], S: ['Soldaten', 5]}"),
 ("\"Aujourd'hui · \"", "'Today · '", "'Heute · '"),
 ("'⏱️ Course aux armements en ce moment : '", "'⏱️ Race to Ace right now: '", "'⏱️ Wettrüsten gerade: '"),
 ("' (aligné sur le duel : compte double)'", "' (matches the duel: counts double)'", "' (passt zum Duell: zählt doppelt)'"),
 ("['Dim.', 'Lun.', 'Mar.', 'Mer.', 'Jeu.', 'Ven.', 'Sam.']", "['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']", "['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa']"),
 ("{t: 'Paris', th: 1}", "{t: 'Paris', th: 1}", "{t: 'MEZ', th: 1}"),
 ("{t: (sl * 4 + 1) + ' h', th: 1}", "{t: ['1 am', '5 am', '9 am', '1 pm', '5 pm', '9 pm'][sl], th: 1}", "{t: (sl * 4 + 1) + ' Uhr', th: 1}"),
 ("['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']", "['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']", "['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']"),
 ("' ·  ce soir'", "' · tonight'", "' · heute Abend'"),
 ("' · cargo fait'", "' · cargo done'", "' · erledigt'"),
 ("'– pas de cargo enregistré'", "'– no cargo recorded'", "'– kein Frachtschiff erfasst'"),
 ("'Champion du VS : à venir, dès que le duel sera relevé.'", "'VS champion: coming once the duel is recorded.'", "'VS-Champion: folgt, sobald das Duell erfasst wird.'"),
 ("'participation ' + r.part + ' / 100'", "'participation ' + r.part + ' / 100'", "'Beteiligung ' + r.part + ' / 100'"),
 ("v(r.p) + ' M de puissance'", "v(r.p) + 'M power'", "v(r.p) + ' Mio. Stärke'"),
 ("' · ensuite : '", "' · next: '", "' · danach: '"),
 ("'Semaine du ' + fr(semaine[0]) + ' au ' + fr(semaine[6]) + \". Classement d'après le relevé du \" + DATA.date + '. Les capitaines déjà passés cette semaine sont écartés des propositions.'", "'Week from ' + fr(semaine[0]) + ' to ' + fr(semaine[6]) + '. Ranking based on the data from ' + DATA.date + '. Captains who already sailed this week are left out of the proposals.'", "'Woche von ' + fr(semaine[0]) + ' bis ' + fr(semaine[6]) + '. Rangliste nach dem Stand vom ' + DATA.date + '. Kapitäne, die diese Woche schon dran waren, werden bei den Vorschlägen ausgelassen.'"),
 ("'Aucun cargo enregistré pour le moment.'", "'No cargo recorded yet.'", "'Noch kein Frachtschiff erfasst.'"),
 ("['Date', 'Capitaine', 'De nouveau possible']", "['Date', 'Captain', 'Possible again']", "['Datum', 'Kapitän', 'Wieder möglich']"),
 ("'✅ oui, depuis le '", "'✅ yes, since '", "'✅ ja, seit '"),
 ("'⏳ à partir du '", "'⏳ from '", "'⏳ ab '"),
 ("'Impossible de charger le classement, réessaie dans un instant.'", "'Could not load the ranking, try again in a moment.'", "'Die Rangliste konnte nicht geladen werden, versuch es gleich noch einmal.'"),
 ("fetch('data.json?v='", "fetch('../data.json?v='", "fetch('../data.json?v='"),
 ("fetch('cargo.json?v='", "fetch('../cargo.json?v='", "fetch('../cargo.json?v='"),
 ("function main(DATA, CARGO) {", "function main(DATA, CARGO) {\nDATA.date = trDate(DATA.date);", "function main(DATA, CARGO) {\nDATA.date = trDate(DATA.date);"),
]
MONTHS = {'en': ['January','February','March','April','May','June','July','August','September','October','November','December'],
          'de': ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']}
TRDATE = {  # « 13 novembre 2026 à 13 h 35 » → date dans la langue
 'en': "function trDate(s){const M=%s,F=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];const m=/^(\\d+)(?:er)? (\\S+) (\\d+)(?: à (\\d+) h ?(\\d*))?/.exec(s);if(!m)return s;const i=F.indexOf(m[2]);if(i<0)return s;return m[1]+' '+M[i]+' '+m[3]+(m[4]?' at '+m[4]+':'+(m[5]||'00').padStart(2,'0')+' (Paris time)':'');}\n",
 'de': "function trDate(s){const M=%s,F=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];const m=/^(\\d+)(?:er)? (\\S+) (\\d+)(?: à (\\d+) h ?(\\d*))?/.exec(s);if(!m)return s;const i=F.indexOf(m[2]);if(i<0)return s;return m[1]+'. '+M[i]+' '+m[3]+(m[4]?' um '+m[4]+':'+(m[5]||'00').padStart(2,'0')+' Uhr (MEZ)':'');}\n"}
ATTR = [('placeholder="Chercher un membre"', 'placeholder="Find a member"', 'placeholder="Mitglied suchen"'),
        ('aria-label="Chercher un membre"', 'aria-label="Find a member"', 'aria-label="Mitglied suchen"'),
        ('aria-label="Filtrer par rang"', 'aria-label="Filter by rank"', 'aria-label="Nach Rang filtern"'),
        ('aria-label="Langue"', 'aria-label="Language"', 'aria-label="Sprache"')]
TITLE = {'en': 'LoVS – tips, rankings and rules', 'de': 'LoVS – Tipps, Rangliste und Regeln'}
problems = []
for col, lang in ((1, 'en'), (2, 'de')):
    D = {norm(k): norm(v) for k, v in json.load(open(os.path.join(ROOT, 'i18n', lang + '.json'), encoding='utf-8')).items()}
    missing = []; parts = []
    for o in out:
        if isinstance(o, str): parts.append(o); continue
        lead, i, trail = o
        key, found = strip_attrs(segs[i])
        tr = D.get(key)
        if tr is None:
            tr = key
            if re.search(r'[a-zà-ÿ]{3}', re.sub(r'<[^>]+>', '', key)) and not re.fullmatch(r'(<[^>]+>|Français|English|Deutsch|\s)+', key): missing.append(key)
        tr = re.sub(r'<(\w+)#(\d+)>', lambda m: found[int(m.group(2))], tr)
        parts.append(lead + tr + trail)
    html = ''.join(parts)
    for t in ATTR:
        if t[0] in html: html = html.replace(t[0], t[col])
    html = re.sub(r'<nav class="lang"[^>]*>.*?</nav>', '<nav class="lang" aria-label="%s">' % ('Language' if lang == 'en' else 'Sprache') +
        ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="true"' if l == lang else '', n) for l, h, n in (('fr', '../', 'Français'), ('en', '../en/', 'English'), ('de', '../de/', 'Deutsch'))) + '</nav>', html, flags=re.S)
    js = tail
    for t in JS:
        if t[0] not in js: problems.append('%s : fragment de script introuvable : %s' % (lang, t[0][:70]))
        js = js.replace(t[0], t[col])
    js = js.replace('<script>\n', '<script>\n' + TRDATE[lang] % json.dumps(MONTHS[lang], ensure_ascii=False), 1)
    h = head.replace('<html lang="fr">', '<html lang="%s">' % lang)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE[lang], h)
    os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
    open(os.path.join(ROOT, lang, 'index.html'), 'w', encoding='utf-8').write(h + html + js)
    print('%s : %d blocs, %d sans traduction' % (lang, len(segs), len(missing)))
    for m in missing: problems.append('%s : pas de traduction pour : %s' % (lang, m[:110]))
for p in problems: print('  !', p)
sys.exit(1 if problems else 0)
