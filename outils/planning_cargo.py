#!/usr/bin/env python3
"""Planning des capitaines du cargo (règle décidée par Yurry).
Lecture : cargo.json -> "planning" {debut, fin, ordre[], week_end}.
Règle : du lundi au vendredi, on suit l'ordre en boucle (un capitaine par soir) ;
samedi et dimanche : « Autres joueurs » (la rotation reprend le lundi, là où elle s'est arrêtée).
Usage : python3 outils/planning_cargo.py [AAAA-MM-JJ fin]   (affiche le planning et vérifie les doublons dans une semaine)
Le même calcul est fait dans index.html (fonction planOf) : modifier "ordre"/"fin" dans cargo.json suffit."""
import json, sys, datetime as dt
c = json.load(open(__file__.rsplit('/', 2)[0] + '/cargo.json'))
p = c['planning']
d = dt.date.fromisoformat(p['debut']); fin = dt.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else p['fin'])
i = 0; sem = {}
while d <= fin:
    if d.weekday() < 5:
        n = p['ordre'][i % len(p['ordre'])]; i += 1
        k = d.isocalendar()[:2]
        if n in sem.setdefault(k, set()): print('⚠ doublon dans la semaine :', n, d)
        sem[k].add(n)
    else: n = p['week_end']
    print(d.isoformat(), d.strftime('%A'), n)
    d += dt.timedelta(1)
