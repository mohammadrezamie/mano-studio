"""Editable circuit documents; compile to the existing logic engine."""
from dataclasses import dataclass
import json
import re
from logic_engine import Circuit, Gate, valid_arity

NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,23}")
MAX_INPUTS = 10
MAX_GATES = 96
MAX_OUTPUTS = 16


def checked_name(name):
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("Use a signal name with 1–24 letters, digits or underscores, starting with a letter.")
    return name


@dataclass(frozen=True)
class CircuitDocument:
    inputs: tuple
    gates: tuple
    outputs: tuple

    @classmethod
    def from_circuit(cls, circuit):
        return cls(circuit.inputs, circuit.gates, circuit.outputs)

    def compile(self):
        if not 1 <= len(self.inputs) <= MAX_INPUTS or len(self.gates) > MAX_GATES or not 1 <= len(self.outputs) <= MAX_OUTPUTS:
            raise ValueError("Circuit size outside supported limits (1–10 inputs, 96 gates, 1–16 outputs).")
        names = set()
        for name in self.inputs + tuple(g.output for g in self.gates):
            checked_name(name)
            if name in names:
                raise ValueError("Duplicate signal: " + name)
            names.add(name)
        for gate in self.gates:
            if not valid_arity(gate.op, len(gate.inputs)):
                raise ValueError("Invalid gate input count: " + gate.output)
            if not set(gate.inputs) <= names:
                raise ValueError("Unconnected or unknown input: " + gate.output)
        output_names = set()
        for name, signal in self.outputs:
            checked_name(name)
            if name in output_names or signal not in names:
                raise ValueError("Duplicate or unconnected output: " + name)
            output_names.add(name)
        known = set(self.inputs)
        pending = list(self.gates)
        ordered = []
        while pending:
            ready = [g for g in pending if set(g.inputs) <= known]
            if not ready:
                raise ValueError("Combinational feedback loop; sequential circuits require a clocked model.")
            for gate in ready:
                ordered.append(gate)
                known.add(gate.output)
                pending.remove(gate)
        return Circuit(self.inputs, tuple(ordered), self.outputs,
                       ("Custom circuit","مدار دلخواه"),
                       ("Editable combinational circuit.","مدار ترکیبی قابل ویرایش."))

    def dumps(self):
        self.compile()
        return json.dumps({"format":"mano-logic","version":1,"inputs":list(self.inputs),
            "gates":[{"output":g.output,"op":g.op,"inputs":list(g.inputs)} for g in self.gates],
            "outputs":[list(o) for o in self.outputs]}, ensure_ascii=False, indent=2)+"\n"

    @classmethod
    def loads(cls, text):
        if len(text) > 200000:
            raise ValueError("Circuit file too large.")
        try:
            obj = json.loads(text)
            if obj["format"] != "mano-logic" or obj["version"] != 1:
                raise ValueError("Unsupported circuit file format.")
            inputs, gates, outputs = obj["inputs"], obj["gates"], obj["outputs"]
            if not all(isinstance(v,list) for v in (inputs,gates,outputs)):
                raise ValueError("Expected arrays.")
            for g in gates:
                if not isinstance(g["inputs"],list):
                    raise ValueError("Expected gate input array.")
            doc = cls(tuple(checked_name(n) for n in inputs),
                tuple(Gate(checked_name(g["output"]),checked_name(g["op"]),
                           tuple(checked_name(n) for n in g["inputs"])) for g in gates),
                tuple((checked_name(n),checked_name(s)) for n,s in outputs))
            doc.compile()
            return doc
        except (KeyError, TypeError, AttributeError, ValueError, RecursionError) as exc:
            raise ValueError("Invalid circuit file: " + str(exc)) from exc
