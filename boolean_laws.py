"""Boolean identities evaluated structurally; no expression evaluation or parser."""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple = ()

    def evaluate(self, env):
        if self.op in ('0', '1'):
            return int(self.op)
        if self.op in ('A', 'B', 'C'):
            value = env[self.op]
            if type(value) is not int or value not in (0, 1):
                raise ValueError('Expected binary input')
            return value
        a = self.args[0].evaluate(env)
        if self.op == 'NOT':
            return 1 - a
        b = self.args[1].evaluate(env)
        if self.op == 'AND':
            return a & b
        if self.op == 'OR':
            return a | b
        raise ValueError('Unknown operation')

    def dual(self):
        op = {'0': '1', '1': '0', 'AND': 'OR', 'OR': 'AND'}.get(self.op, self.op)
        return Expr(op, tuple(a.dual() for a in self.args))

    def __str__(self):
        if not self.args:
            return self.op
        if self.op == 'NOT':
            return str(self.args[0]) + "'"
        return '(' + (' · ' if self.op == 'AND' else ' + ').join(map(str, self.args)) + ')'


def AND(a, b): return Expr('AND', (a, b))
def OR(a, b): return Expr('OR', (a, b))
def NOT(a): return Expr('NOT', (a,))


A, B, C, ZERO, ONE = map(Expr, ('A', 'B', 'C', '0', '1'))


@dataclass(frozen=True)
class Law:
    id: str
    title: tuple[str, str]
    left: Expr
    right: Expr


LAWS = (
    Law('identity', ('Identity', 'همانی'), OR(A, ZERO), A),
    Law('domination', ('Domination', 'غلبه'), OR(A, ONE), ONE),
    Law('idempotent', ('Idempotence', 'خودتوانی'), OR(A, A), A),
    Law('complement', ('Complement', 'متمم'), OR(A, NOT(A)), ONE),
    Law('involution', ('Double negation', 'نفی مضاعف'), NOT(NOT(A)), A),
    Law('commutative', ('Commutativity', 'جابجایی'), OR(A, B), OR(B, A)),
    Law('associative', ('Associativity', 'شرکت‌پذیری'), OR(OR(A, B), C), OR(A, OR(B, C))),
    Law('distributive', ('Distributivity', 'توزیع‌پذیری'), AND(A, OR(B, C)), OR(AND(A, B), AND(A, C))),
    Law('absorption', ('Absorption', 'جذب'), OR(A, AND(A, B)), A),
    Law('de-morgan', ('De Morgan', 'دمورگان'), NOT(OR(A, B)), AND(NOT(A), NOT(B))),
    Law('consensus', ('Consensus', 'اجماع'), OR(OR(AND(A, B), AND(NOT(A), C)), AND(B, C)), OR(AND(A, B), AND(NOT(A), C))),
    Law('combining', ('Combining', 'ترکیب'), OR(AND(A, B), AND(A, NOT(B))), A),
)
BY_ID = {law.id: law for law in LAWS}


def compare(law_id, dual=False):
    """Return expressions and all eight input rows, with independent sides."""
    if law_id not in BY_ID or type(dual) is not bool:
        raise ValueError('Unknown law or dual selector')
    law = BY_ID[law_id]
    left, right = law.left, law.right
    if dual:
        left, right = left.dual(), right.dual()
    rows = tuple((*bits, left.evaluate(env), right.evaluate(env))
                 for bits in product((0, 1), repeat=3)
                 for env in [dict(zip('ABC', bits))])
    return left, right, rows
