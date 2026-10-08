# Télécharge les matchs du Barça en Liga (StatsBomb, 2004-05 à 2020-21) et garde uniquement les tirs.
import json, urllib.request, sys, os, time
B='https://raw.githubusercontent.com/statsbomb/open-data/master/data/'
def get(u):
    for k in range(4):
        try: return json.load(urllib.request.urlopen(B+u, timeout=60))
        except Exception as e:
            time.sleep(2**k); err=e
    raise err
OUT=sys.argv[1]
comps=[c for c in get('competitions.json') if c['competition_id']==11 and c['season_name']!='1973/1974']
rows=[]; done=set()
if os.path.exists(OUT):
    rows=json.load(open(OUT)); done={r['match_id'] for r in rows}
for c in comps:
    ms=get(f"matches/11/{c['season_id']}.json")
    for m in ms:
        if m['match_id'] in done: continue
        ev=get(f"events/{m['match_id']}.json")
        for e in ev:
            if e['type']['name']=='Shot':
                s=e['shot']
                rows.append({'match_id':m['match_id'],'saison':c['season_name'],'joueur':e['player']['name'],'equipe':e['team']['name'],
                 'xg':s.get('statsbomb_xg'),'resultat':s['outcome']['name'],'type':s['type']['name'],'loc':e.get('location'),'partie':s['body_part']['name']})
        rows.append({'match_id':m['match_id'],'marqueur':True})
        done.add(m['match_id'])
    json.dump(rows,open(OUT,'w'))
    print(c['season_name'],len(ms),flush=True)
json.dump(rows,open(OUT,'w')); print('fini')
