"""Reachability and exact behavioral equivalence of complete binary FSMs."""
from collections import deque
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Analysis:
    paths: tuple
    unreachable: tuple
    classes: tuple
    witnesses: tuple


def analyze_machine(model):
    """Analyze output sequences sampled before each clock, from reset Q=0.

    Paths and distinguishing words are shortest, with binary lexical ties.
    Classes include all encoded states, even unreachable ones. Nothing is edited.
    """
    size = 2**model.bits
    states = tuple(range(size))
    transitions = {(q,x): model.step(q,x) for q in states for x in (0,1)}
    paths = {0: ''}
    queue = deque([0])
    while queue:
        q = queue.popleft()
        for x in (0,1):
            nxt,_ = transitions[q,x]
            if nxt not in paths:
                paths[nxt] = paths[q] + str(x)
                queue.append(nxt)

    def distinguish(a,b):
        queue = deque([(a,b,'')])
        seen = {(a,b)}
        while queue:
            p,q,word = queue.popleft()
            for x in (0,1):
                pn,py = transitions[p,x]
                qn,qy = transitions[q,x]
                candidate = word + str(x)
                if py != qy:
                    return candidate
                pair = tuple(sorted((pn,qn)))
                if pn != qn and pair not in seen:
                    seen.add(pair)
                    queue.append((*pair,candidate))
        return None

    witnesses = {(a,b): distinguish(a,b) for a,b in combinations(states,2)}
    classes = []
    for q in states:
        for group in classes:
            if witnesses[group[0],q] is None:
                group.append(q)
                break
        else:
            classes.append([q])
    return Analysis(tuple(sorted(paths.items())), tuple(q for q in states if q not in paths),
                    tuple(tuple(g) for g in classes),
                    tuple((a,b,word) for (a,b),word in witnesses.items()))
