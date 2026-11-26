"""Native bus experiment checkpoint with bounded, model-replayed history."""
from databus_lab import Databus, REGISTERS, SOURCES, DESTINATIONS, event_controls
from word_arithmetic import OPERATIONS
import mano_file


def words(value, count):
    if not isinstance(value, list) or len(value) != count or any(type(v) is not int or not 0 <= v < 16 for v in value):
        raise ValueError("Invalid bus checkpoint words")
    return value


def controls(value):
    if not isinstance(value, dict) or set(value) not in ({"sources", "destinations", "external"}, {"sources", "destinations", "external", "operation", "carry"}):
        raise ValueError("Invalid bus controls")
    for key, allowed in (("sources", SOURCES), ("destinations", DESTINATIONS)):
        pins = value[key]
        if not isinstance(pins, list) or any(not isinstance(p, str) or p not in allowed for p in pins) or len(set(pins)) != len(pins):
            raise ValueError("Invalid bus pin selection")
    external = value["external"]
    if type(external) is not int or not 0 <= external < 16:
        raise ValueError("Invalid external word")
    operation, carry = value.get("operation", "ADD"), value.get("carry", 0)
    if operation not in OPERATIONS or type(carry) is not int or carry not in (0,1):
        raise ValueError("Invalid ALU controls")
    return event_controls(tuple(value["sources"]), tuple(value["destinations"]), external, operation, carry)


def control_record(sources, destinations, external, operation="ADD", carry=0):
    obj = {"sources": list(sources), "destinations": list(destinations), "external": external}
    if operation != "ADD" or type(carry) is not int or carry != 0:
        obj.update(operation=operation, carry=carry)
    return obj


def snapshot(model, staged):
    # Rewind retained writes to derive the state immediately before the
    # oldest retained event. The discarded prefix need not be serialized.
    ram = [model.memory.read(a) for a in range(16)]
    for cycle in reversed(model.history):
        if cycle.memory_write is not None:
            address, old, _ = cycle.memory_write
            ram[address] = old
    base = list(model.history[0].before if model.history else model.registers.values())
    return {"registers": base, "ram": ram,
            "events": [control_record(*event) for event in model.events],
            "controls": control_record(*staged)}


def restore(payload):
    if not isinstance(payload, dict) or set(payload) != {"registers", "ram", "events", "controls"}:
        raise ValueError("Invalid bus checkpoint")
    base = words(payload["registers"], 3)
    ram = words(payload["ram"], 16)
    events = payload["events"]
    if not isinstance(events, list) or len(events) > 64:
        raise ValueError("Invalid bus history length")
    staged = controls(payload["controls"])
    # Construct a fresh model; the caller replaces the live model only
    # after every accepted event has been replayed successfully.
    model = Databus()
    model.registers.update(zip(REGISTERS, base))
    for address, word in enumerate(ram):
        model.memory.write(address, word)
    for event in events:
        model.tick(*controls(event))
    return model, staged


def save(path, model, staged):
    payload = snapshot(model, staged)
    restore(payload)
    mano_file.save(path, "databus", payload)


def load(path):
    kind, payload = mano_file.load(path)
    if kind != "databus":
        raise ValueError("Expected a bus experiment")
    return restore(payload)
