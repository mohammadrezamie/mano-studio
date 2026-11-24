"""Offline combinational logic engine; gates are the source of truth.

A circuit is a topologically ordered netlist of named one-bit signals.
Both the diagram and truth table consume exactly this netlist.
"""
from dataclasses import dataclass
from itertools import product
from types import MappingProxyType

ARITY = {"NOT": 1, "AND": 2, "OR": 2, "XOR": 2, "NAND": 2, "NOR": 2, "XNOR": 2}


def gate_value(op, *bits):
    if op not in ARITY or len(bits) != ARITY[op] or any(b not in (0, 1) for b in bits):
        raise ValueError("Invalid gate or inputs")
    a = bits[0]
    if op == "NOT":
        return 1-a
    b = bits[1]
    return {"AND": a & b, "OR": a | b, "XOR": a ^ b,
            "NAND": 1-(a & b), "NOR": 1-(a | b), "XNOR": 1-(a ^ b)}[op]


@dataclass(frozen=True)
class Gate:
    output: str
    op: str
    inputs: tuple[str, ...]


@dataclass(frozen=True)
class Circuit:
    inputs: tuple[str, ...]
    gates: tuple[Gate, ...]
    outputs: tuple[tuple[str, str], ...]
    title: tuple[str, str]
    explanation: tuple[str, str]

    def __post_init__(self):
        known = set(self.inputs)
        if len(known) != len(self.inputs):
            raise ValueError("Duplicate input")
        for gate in self.gates:
            if gate.output in known or ARITY.get(gate.op) != len(gate.inputs) or not set(gate.inputs) <= known:
                raise ValueError("Invalid, cyclic or unordered gate netlist")
            known.add(gate.output)
        if len({name for name, _ in self.outputs}) != len(self.outputs) or any(signal not in known for _,signal in self.outputs):
            raise ValueError("Invalid output mapping")

    def evaluate(self, inputs):
        if set(inputs) != set(self.inputs) or any(v not in (0,1) for v in inputs.values()):
            raise ValueError("Supply exactly the binary inputs")
        values = dict(inputs)
        for gate in self.gates:
            values[gate.output] = gate_value(gate.op, *(values[i] for i in gate.inputs))
        return MappingProxyType(values)

    def result(self, inputs):
        values = self.evaluate(inputs)
        return {name: values[signal] for name,signal in self.outputs}

    def truth_table(self):
        if len(self.inputs) > 10:
            raise ValueError("Truth table too large")
        for bits in product((0,1), repeat=len(self.inputs)):
            yield bits, tuple(self.result(dict(zip(self.inputs,bits))).values())


def g(output, op, *inputs):
    return Gate(output, op, inputs)


def basic(op):
    inputs = ("A",) if op == "NOT" else ("A","B")
    return Circuit(inputs,(g("q",op,*inputs),),(("Y","q"),),
                   (op,op),("One elementary logic gate.", "یک گیت منطقی پایه."))


CIRCUITS = {op.lower(): basic(op) for op in ARITY}
CIRCUITS.update({
    "half_adder": Circuit(("A","B"),(g("sum","XOR","A","B"),g("carry","AND","A","B")),
        (("S","sum"),("C","carry")),("Half adder","نیم‌جمع‌کننده"),
        ("S = A XOR B; C = A AND B.", "جمع دو بیت؛ S حاصل جمع و C نقلی است.")),
    "full_adder": Circuit(("A","B","Cin"),(
        g("p","XOR","A","B"),g("g","AND","A","B"),
        g("sum","XOR","p","Cin"),g("h","AND","p","Cin"),g("carry","OR","g","h")),
        (("S","sum"),("Cout","carry")),("Full adder","تمام‌جمع‌کننده"),
        ("Two half adders and an OR gate add three bits.", "دو نیم‌جمع‌کننده و یک OR سه بیت را جمع می‌کنند.")),
    "decoder": Circuit(("A1","A0"),(g("n1","NOT","A1"),g("n0","NOT","A0"),
        g("d0","AND","n1","n0"),g("d1","AND","n1","A0"),
        g("d2","AND","A1","n0"),g("d3","AND","A1","A0")),
        tuple((f"Y{i}",f"d{i}") for i in range(4)),("2-to-4 decoder","دیکودر ۲ به ۴"),
        ("Exactly one active-high output is selected by the binary address.", "آدرس دودویی دقیقاً یک خروجی فعال را انتخاب می‌کند.")),
    "encoder": Circuit(("D0","D1","D2","D3"),(
        g("hi","OR","D2","D3"),g("lo","OR","D1","D3"),
        g("any01","OR","D0","D1"),g("any23","OR","D2","D3"),g("any","OR","any01","any23"),
        g("pair01","AND","D0","D1"),g("pair23","AND","D2","D3"),
        g("cross","AND","any01","any23"),g("pair","OR","pair01","pair23"),
        g("multiple","OR","pair","cross"),g("single","NOT","multiple"),g("valid","AND","any","single")),
        (("Y1","hi"),("Y0","lo"),("Valid","valid")),("4-to-2 encoder","انکودر ۴ به ۲"),
        ("One-hot encoder: Y is meaningful only when Valid = 1.", "انکودر معمولی؛ خروجی فقط وقتی معتبر است که دقیقاً یک ورودی فعال باشد.")),
    "mux": Circuit(("D0","D1","S"),(g("ns","NOT","S"),g("p0","AND","D0","ns"),
        g("p1","AND","D1","S"),g("y","OR","p0","p1")),(("Y","y"),),
        ("2-to-1 multiplexer","مالتی‌پلکسر ۲ به ۱"),("S selects D0 or D1.", "S یکی از دو ورودی داده را انتخاب می‌کند.")),
    "demux": Circuit(("D","S"),(g("ns","NOT","S"),g("y0","AND","D","ns"),g("y1","AND","D","S")),
        (("Y0","y0"),("Y1","y1")),("1-to-2 demultiplexer","دی‌مالتی‌پلکسر ۱ به ۲"),
        ("S directs D to one output.", "S مسیر داده را به یکی از خروجی‌ها تعیین می‌کند.")),
    "half_subtractor": Circuit(("A","B"),(g("na","NOT","A"),g("diff","XOR","A","B"),g("borrow","AND","na","B")),
        (("D","diff"),("Borrow","borrow")),("Half subtractor","نیم‌تفریق‌کننده"),
        ("Subtract B from A.", "تفریق B از A.")),
})


def ripple_adder(width=4):
    if not 1 <= width <= 8:
        raise ValueError("Width must be 1–8")
    gates = []
    carry = "Cin"
    for i in range(width):
        a,b = f"A{i}",f"B{i}"
        p,h,j,s,c = (f"{name}{i}" for name in ("p","h","j","s","c"))
        gates.extend((g(p,"XOR",a,b),g(h,"AND",a,b),g(s,"XOR",p,carry),
                      g(j,"AND",p,carry),g(c,"OR",h,j)))
        carry = c
    return Circuit(tuple(f"A{i}" for i in range(width))+tuple(f"B{i}" for i in range(width))+("Cin",),
        tuple(gates),tuple((f"S{i}",f"s{i}") for i in range(width))+(("Cout",carry),),
        (f"{width}-bit ripple adder",f"جمع‌کننده {width} بیتی"),
        ("Carry propagates through cascaded full adders, LSB first.", "نقلی از بیت کم‌ارزش به بیت پرارزش منتقل می‌شود."))


CIRCUITS["ripple4"] = ripple_adder()
