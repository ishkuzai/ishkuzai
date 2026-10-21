# -*- coding: utf-8 -*-
"""Export law-by-law traces for a few senses (read-only use of the engine)."""
import json, sys
import build_all, tuglemca
from laws import pie
import varnas_morph as M

WANT = ['wolf', 'fire', 'stone', 'horse', 'king', 'word', 'water', 'god']
L = build_all.build()
D = {x['gloss']: x for x in L}
out = {'laws': [], 'words': []}
for stage, dates, note, laws in tuglemca.STAGES:
    for lid, name, text, _ in laws:
        out['laws'].append(dict(id=lid, name=name, text=text, stage=stage, dates=dates))
out['stages'] = [dict(name=s, dates=d, note=n) for s, d, n, _ in tuglemca.STAGES]
for g in WANT:
    if g not in D:
        print('missing', g, file=sys.stderr)
        continue
    x = D[g]
    st = M.stressed(x['protoform'])
    steps = [dict(stage=s, law=l, name=n, form=f, changed=bool(c))
             for s, l, n, f, c in tuglemca.trace(st)]
    steps[0]['form'] = pie(steps[0]['form'])
    out['words'].append(dict(gloss=g, root=pie(x['proto']), protoform=pie(x['protoform']),
                             rakva_citation=x['rakwa'], stages=tuglemca.stage_forms(st),
                             steps=steps))
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
