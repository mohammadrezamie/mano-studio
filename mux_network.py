"""Structural Shannon expansion into 2:1 MUX cells using ordinary gates."""


def network(values):
    """Return input names, gate triples, F mapping, and explicit MUX stages.

    Input order is MSB first. Only complete binary tables are accepted.
    Identical cofactors share a signal; equal branches eliminate a MUX.
    Constants are generated from a variable and its complement.
    """
    values = tuple(values)
    n = {4: 2, 8: 3, 16: 4}.get(len(values))
    if n is None or any(type(v) is not int or v not in (0, 1) for v in values):
        raise ValueError('Expected a complete 2–4 variable binary truth table')
    inputs = tuple('ABCD'[:n])
    gates, stages = [], []
    inverses, constants, cache = {}, {}, {}

    def add(op, *args):
        name = f'm{len(gates)+1}'
        gates.append((name, op, args))
        return name

    def inverse(name):
        if name not in inverses:
            inverses[name] = add('NOT', name)
        return inverses[name]

    def constant(bit):
        if bit not in constants:
            a = inputs[0]
            constants[bit] = add('OR' if bit else 'AND', a, inverse(a))
        return constants[bit]

    def solve(level, table):
        key = (level, table)
        if key in cache:
            return cache[key]
        if len(set(table)) == 1:
            result = constant(table[0])
        else:
            half = len(table)//2
            select = inputs[level]
            low = solve(level+1, table[:half])
            high = solve(level+1, table[half:])
            if low == high:
                result = low
            else:
                p = add('AND', inverse(select), low)
                q = add('AND', select, high)
                result = add('OR', p, q)
                stages.append((select, low, high, result))
        cache[key] = result
        return result

    output = solve(0, values)
    return inputs, tuple(gates), (('F', output),), tuple(stages)
