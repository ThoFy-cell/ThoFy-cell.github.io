#!/usr/bin/env python3
"""Met à jour data.json avec un nouveau relevé en gardant les deux relevés précédents (3 au total).
Usage : python3 outils/maj_data.py membres.csv "14 novembre 2026 à 19 h"
Le relevé actuel de data.json passe en tête de « historique » ; on n'en garde que 2.
Colonnes du CSV : membre,rang,classement_aide,classement_dons,sieges_semaine,classement_eliminations,coffres_semaine,puissance_M"""
import csv, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src, date = sys.argv[1:3]
path = os.path.join(ROOT, 'data.json')
num = lambda x: float(x) if x not in ('', None) else None
m = [dict(n=r['membre'], r=r['rang'], a=num(r['classement_aide']), d=num(r['classement_dons']), s=num(r['sieges_semaine']),
          e=num(r['classement_eliminations']), c=num(r['coffres_semaine']), p=num(r['puissance_M'])) for r in csv.DictReader(open(src, encoding='utf-8'))]
old = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None
hist = []
if old and old.get('date') != date:
    hist = [{'date': old['date'], 'membres': old['membres']}] + old.get('historique', [])
elif old:
    hist = old.get('historique', [])
json.dump({'date': date, 'membres': m, 'historique': hist[:2]}, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(date, len(m), 'membres ; historique :', [h['date'] for h in hist[:2]])
