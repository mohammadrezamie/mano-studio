from itertools import permutations
from random import Random
import pytest
from omega_network import route, transfer_round


@pytest.mark.parametrize("size", [2, 4, 8, 16, 32, 64])
def test_all_paths(size):
    for source in range(size):
        for destination in range(size):
            hops = route(size, source, destination)
            assert len(hops) == size.bit_length() - 1
            assert hops[0].input_line == source
            assert hops[-1].output_line == destination
            for i, hop in enumerate(hops):
                assert hop.stage == i
                assert hop.input_line // 2 == hop.output_line // 2
                assert hop.output_line % 2 == int(f"{destination:0{len(hops)}b}"[i])
                if i + 1 < len(hops):
                    bits = f"{hop.output_line:0{len(hops)}b}"
                    assert hops[i + 1].input_line == int(bits[1:] + bits[0], 2)


def test_internal_block_with_distinct_destinations():
    a, b = transfer_round(8, [(1, 1), (0, 0)])
    assert a.granted and not b.granted
    assert b.blocked_stage == 0 and b.blocked_by == 0


def test_switch_can_cross_both_ports():
    a, b = transfer_round(2, [(0, 1), (1, 0)])
    assert all(t.granted and t.hops[0].crossed for t in (a, b))


def check_round(size, requests):
    results = transfer_round(size, requests)
    assert results == transfer_round(size, reversed(requests))
    accepted = {}
    for t in results:
        links = [(h.stage, h.output_line) for h in t.hops]
        overlaps = [link for link in links if link in accepted]
        assert t.granted == (not overlaps)
        if overlaps:
            assert t.blocked_stage == overlaps[0][0]
            assert t.blocked_by == accepted[overlaps[0]]
        else:
            accepted.update((link, t.source) for link in links)


def test_all_four_port_permutations():
    for destinations in permutations(range(4)):
        check_round(4, list(enumerate(destinations)))


@pytest.mark.parametrize("size", [8, 16, 32, 64])
def test_seeded_rounds(size):
    rng = Random(size)
    for _ in range(100):
        check_round(size, [(s, rng.randrange(size)) for s in range(size)])


@pytest.mark.parametrize("size,requests", [(3, []), (True, []), (4, [(0, 4)]),
    (4, [(True, 1)]), (4, [(0, 1), (0, 2)]), (4, [(-1, 2)])])
def test_rejected_input(size, requests):
    with pytest.raises(ValueError):
        transfer_round(size, requests)
