import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import story
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
d = story.build()
json.dump(d, open(os.path.join(ROOT, 'src/main/resources/realmbreak_story.json'), 'w'), indent=1)
# validate
import manifest as M
items = {i['id'] for i in M.ITEMS} | {b['id'] for b in M.BLOCKS}
bad = []
for q in d['quests']:
    for r in q['rewards'] + q['give']:
        if ':' not in r['id'] and r['id'] not in items:
            bad.append((q['id'], r['id']))
    for o in q['objectives']:
        if o['type'] == 'collect' and ':' not in o['target'] and o['target'] not in items:
            bad.append((q['id'], o['target']))
for k, v in d['npcs'].items():
    for t in v['trades']:
        for c in t['cost'] + [t['result']]:
            if ':' not in c['id'] and c['id'] not in items:
                bad.append((k, c['id']))
print(len(d['quests']), 'quests; bad ids:', bad)
