"""Offline combinational logic engine; gates are the source of truth.

A circuit is a topologically ordered netlist of named one-bit signals.
Both the diagram and truth table consume exactly this netlist.
"""
from dataclasses import dataclass
from itertools import product
from types import MappingProxyType

ARITY = {"NOT": 1, "AND": 2, "OR": 2, "XOR": 2, "NAND": 2, "NOR": 2, "XNOR": 2}


def valid_arity(op, count):
    return (op == "NOT" and count == 1) or (op in ARITY and op != "NOT" and 2 <= count <= 4)


def gate_value(op, *bits):
    if not valid_arity(op, len(bits)) or any(b not in (0, 1) for b in bits):
        raise ValueError("Invalid gate or inputs")
    a = bits[0]
    if op == "NOT":
        return 1-a
    conjunction = int(all(bits))
    disjunction = int(any(bits))
    parity = sum(bits) % 2
    return {"AND": conjunction, "OR": disjunction, "XOR": parity,
            "NAND": 1-conjunction, "NOR": 1-disjunction, "XNOR": 1-parity}[op]


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
            if gate.output in known or not valid_arity(gate.op, len(gate.inputs)) or not set(gate.inputs) <= known:
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


def basic(op, count=None):
    count = ARITY[op] if count is None else count
    if not valid_arity(op, count):
        raise ValueError("Unsupported input count")
    inputs = tuple("ABCD"[:count])
    return Circuit(inputs,(g("q",op,*inputs),),(("Y","q"),),
                   (op,op),("One elementary logic gate. Multi-input XOR/XNOR use odd/even parity.", "یک گیت پایه؛ XOR و XNOR چندورودی بر اساس زوج یا فرد بودن تعداد بیت‌های یک عمل می‌کنند."))


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


def carry_lookahead_adder(width=4):
    """Use the structural prefix expansion in the shared circuit engine."""
    from carry_lookahead import network
    inputs, triples, outputs = network(width)
    return Circuit(inputs, tuple(Gate(name, op, args) for name, op, args in triples), outputs,
        (f"{width}-bit carry look-ahead adder", f"جمع‌کننده {width} بیتی نقلی پیش‌بین"),
        ("XOR propagate and AND generate; expanded prefix carry equations use Cin directly. Ideal gate levels, not physical delay.",
         "انتشار با XOR و تولید با AND؛ معادلات پیش‌بین مستقیماً از Cin استفاده می‌کنند. سطح منطقی ایده‌آل است، نه تأخیر فیزیکی."))


CIRCUITS["lookahead4"] = carry_lookahead_adder()



def expanded_decoder(width=3, active_low=False):
    """Active-high enable, binary select; inactive outputs are the opposite level."""
    if width not in (2,3):
        raise ValueError("Decoder width must be 2 or 3")
    inputs=tuple(f"A{i}" for i in reversed(range(width)))
    gates=[g(f"n{i}","NOT",f"A{i}") for i in range(width)]
    for value in range(1<<width):
        literals=tuple(f"A{i}" if value&(1<<i) else f"n{i}" for i in reversed(range(width)))
        gates.append(g(f"y{value}","NAND" if active_low else "AND",*literals,"EN"))
    polarity="active-low" if active_low else "active-high"
    return Circuit(inputs+("EN",),tuple(gates),tuple((f"Y{i}",f"y{i}") for i in range(1<<width)),
        (f"{width}-to-{1<<width} decoder ({polarity})",f"دیکودر {width} به {1<<width} (فعال با {'صفر' if active_low else 'یک'})"),
        ("EN=1 selects exactly one output; EN=0 leaves all outputs inactive.",
         "با EN=1 فقط خروجی متناظر با آدرس فعال است؛ با EN=0 همه خروجی‌ها غیرفعال‌اند."))


def multiplexer4():
    gates=[g("ns0","NOT","S0"),g("ns1","NOT","S1")]
    for i in range(4):
        gates.append(g(f"p{i}","AND",f"D{i}","S1" if i&2 else "ns1","S0" if i&1 else "ns0"))
    gates.append(g("y","OR","p0","p1","p2","p3"))
    return Circuit(("D0","D1","D2","D3","S1","S0"),tuple(gates),(("Y","y"),),
        ("4-to-1 multiplexer","مالتی‌پلکسر ۴ به ۱"),
        ("Y = D[2×S1 + S0].","آدرس دودویی S1 و S0 یکی از چهار ورودی را انتخاب می‌کند."))


def priority_encoder4():
    gates=(g("n3","NOT","D3"),g("n2","NOT","D2"),
           g("p1","AND","D1","n2","n3"),g("hi","OR","D3","D2"),
           g("lo","OR","D3","p1"),g("valid","OR","D0","D1","D2","D3"))
    return Circuit(("D0","D1","D2","D3"),gates,(("Y1","hi"),("Y0","lo"),("Valid","valid")),
        ("4-to-2 priority encoder","انکودر اولویت‌دار ۴ به ۲"),
        ("D3 has highest priority. Valid=0 means no active input.",
         "D3 بیشترین اولویت را دارد. Valid=0 یعنی هیچ ورودی فعالی وجود ندارد."))


def comparator(width=2):
    if width not in (2,4):
        raise ValueError("Comparator width must be 2 or 4")
    gates=[]
    for i in range(width):
        gates.extend((g(f"eq{i}","XNOR",f"A{i}",f"B{i}"),
                      g(f"na{i}","NOT",f"A{i}"),g(f"nb{i}","NOT",f"B{i}"),
                      g(f"lt{i}","AND",f"na{i}",f"B{i}"),g(f"gt{i}","AND",f"A{i}",f"nb{i}")))
    eq="eq0";lt="lt0";gt="gt0"
    for i in range(1,width):
        gates.extend((g(f"lpass{i}","AND",f"eq{i}",lt),g(f"gpass{i}","AND",f"eq{i}",gt),
                      g(f"less{i}","OR",f"lt{i}",f"lpass{i}"),g(f"greater{i}","OR",f"gt{i}",f"gpass{i}"),
                      g(f"equal{i}","AND",f"eq{i}",eq)))
        eq,lt,gt=f"equal{i}",f"less{i}",f"greater{i}"
    return Circuit(tuple(f"A{i}" for i in range(width))+tuple(f"B{i}" for i in range(width)),tuple(gates),
        (("LT",lt),("EQ",eq),("GT",gt)),(f"{width}-bit magnitude comparator",f"مقایسه‌گر {width} بیتی"),
        ("Unsigned comparison; the highest unequal bit decides the result.",
         "مقایسه بدون علامت؛ پرارزش‌ترین بیت متفاوت نتیجه را تعیین می‌کند."))


CIRCUITS.update({
    "decoder3":expanded_decoder(3),
    "decoder_nand":expanded_decoder(2,True),
    "mux4":multiplexer4(),
    "priority4":priority_encoder4(),
    "compare2":comparator(2),
    "compare4":comparator(4),
    "full_subtractor":Circuit(("A","B","Bin"),
        (g("p","XOR","A","B"),g("diff","XOR","p","Bin"),g("na","NOT","A"),
         g("np","NOT","p"),g("b0","AND","na","B"),g("b1","AND","np","Bin"),g("borrow","OR","b0","b1")),
        (("D","diff"),("Bout","borrow")),("Full subtractor","تمام‌تفریق‌کننده"),
        ("A − B − Bin = D − 2×Bout.","تفریق دو بیت با قرض ورودی؛ D نتیجه و Bout قرض خروجی است.")),
    "parity4":Circuit(("A","B","C","D"),(g("odd","XOR","A","B","C","D"),g("even","NOT","odd")),
        (("Odd","odd"),("Even","even")),("4-bit parity detector","تشخیص زوجیت ۴ بیتی"),
        ("Odd=1 for an odd number of ones; Even is its complement.",
         "Odd برای تعداد فرد بیت‌های یک فعال است؛ Even مکمل آن است.")),
})


def gate_equation(gate):
    """Canonical local Boolean expression derived from actual gate inputs."""
    terms=gate.inputs
    op=gate.op
    if op=="NOT":
        rhs="¬"+terms[0]
    else:
        family={"NAND":"AND","NOR":"OR","XNOR":"XOR"}.get(op,op)
        symbol={"AND":" ∧ ","OR":" ∨ ","XOR":" ⊕ "}[family]
        rhs=symbol.join(terms)
        if op in ("NAND","NOR","XNOR"):
            rhs="¬("+rhs+")"
    return gate.output+" = "+rhs


def circuit_equations(circuit):
    return tuple(gate_equation(gate) for gate in circuit.gates)+tuple(f"{name} = {signal}" for name,signal in circuit.outputs)
