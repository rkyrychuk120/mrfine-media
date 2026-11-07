import json
O=json.load(open('timeline_v1.json'))['clips']; N=json.load(open('timeline.json'))
NC=N['clips']
def _pts():
    p=[(0.0,0.0)]
    for o,n in zip(O,NC):
        p.append((n['start'],o['start'])); p.append((n['start']+n['dur'],o['start']+o['dur']))
    p.append((N['total'],113.36)); return p
P=_pts()
def new2old(t):
    for (a,oa),(b,ob) in zip(P,P[1:]):
        if t<=b: return oa+(t-a)*(ob-oa)/max(1e-6,(b-a))
    return P[-1][1]
def old2new(t):
    for (a,oa),(b,ob) in zip(P,P[1:]):
        if t<=ob: return a+(t-oa)*(b-a)/max(1e-6,(ob-oa))
    return P[-1][0]
