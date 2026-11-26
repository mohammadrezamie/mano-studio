"""Pure combinational block insertion plan, with explicit input bindings."""
import re


def insert(base_inputs, base_gates, base_outputs, block_inputs, block_gates,
           block_outputs, prefix, bindings):
    """Gate triples are (output, op, inputs); output pairs are (name, source).

    None exposes a new input. Other bindings refer only to existing signals.
    Existing inputs, gates and output aliases remain unchanged.
    The caller validates both source documents and compiles the result.
    """
    if not isinstance(prefix, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,11}', prefix):
        raise ValueError('Invalid block prefix (1–12 ASCII identifier characters)')
    if set(bindings) != set(block_inputs):
        raise ValueError('Supply exactly one binding per block input')
    known = set(base_inputs) | {name for name, _, _ in base_gates}
    used = known | {name for name, _ in base_outputs}
    mapping = {}
    inputs, gates, outputs = list(base_inputs), list(base_gates), list(base_outputs)

    def fresh(name):
        result = prefix + '_' + name
        if len(result) > 24 or result in used:
            raise ValueError('Block name collision or length limit: ' + result)
        used.add(result)
        return result

    for name in block_inputs:
        source = bindings[name]
        if source is None:
            source = fresh(name)
            inputs.append(source)
        elif not isinstance(source, str) or source not in known:
            raise ValueError('Unknown existing input signal')
        mapping[name] = source
    for name, op, args in block_gates:
        result = fresh(name)
        gates.append((result, op, tuple(mapping[a] for a in args)))
        mapping[name] = result
    for name, source in block_outputs:
        # A valid source document may name an output alias exactly like its
        # underlying signal. Preserve that alias when it is our new signal,
        # while still rejecting collisions with unrelated names.
        alias = prefix + '_' + name
        if name == source and mapping[source] == alias and alias not in known:
            outputs.append((alias, alias))
        else:
            outputs.append((fresh(name), mapping[source]))
    if len(inputs) > 10 or len(gates) > 96 or len(outputs) > 16:
        raise ValueError('Combined circuit exceeds editor limits')
    return tuple(inputs), tuple(gates), tuple(outputs)
