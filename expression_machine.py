"""Chapter 8 educational address-count formats, not a machine-code ISA."""
import re
from dataclasses import dataclass
from cpu_organization import RegisterStack
from word_arithmetic import alu, signed

OPS={"+":"ADD","-":"SUB","*":"MUL","/":"DIV"}
PRECEDENCE={"+":1,"-":1,"*":2,"/":2}


def postfix(source):
    """Shunting-yard conversion; binary operators, A–D, decimal words."""
    if len(source)>512:
        raise ValueError("Expression too long")
    source=source.strip().upper()
    tokens=re.findall(r"[0-9]+|[A-D]|[()+*/-]|[^\s]",source)
    if not tokens or len(tokens)>127:
        raise ValueError("Invalid expression length")
    output,operators=[],[]
    expect_operand=True
    for token in tokens:
        if token in ("A","B","C","D") or token.isascii() and token.isdecimal():
            if not expect_operand:raise ValueError("Expected operator")
            if token.isdecimal() and int(token)>65535:raise ValueError("Literal outside word")
            output.append(token);expect_operand=False
        elif token=="(":
            if not expect_operand:raise ValueError("Expected operator")
            operators.append(token)
        elif token==")":
            if expect_operand:raise ValueError("Expected operand")
            while operators and operators[-1]!="(":output.append(operators.pop())
            if not operators:raise ValueError("Unmatched parenthesis")
            operators.pop()
        elif token in OPS:
            if expect_operand:raise ValueError("Expected operand")
            while operators and operators[-1] in OPS and PRECEDENCE[operators[-1]]>=PRECEDENCE[token]:
                output.append(operators.pop())
            operators.append(token);expect_operand=True
        else:raise ValueError("Invalid token")
    if expect_operand:raise ValueError("Expected operand")
    while operators:
        op=operators.pop()
        if op=="(":raise ValueError("Unmatched parenthesis")
        output.append(op)
    return tuple(output)


def compile_expression(tokens,addresses):
    """Generate original pseudo-instructions, temporaries are abstract storage."""
    if addresses not in (0,1,2,3):raise ValueError("Invalid format")
    code=[];pending=[];count=0
    for token in tokens:
        if token not in OPS:
            if addresses==0:code.append(("PUSH",token))
            pending.append(token)
            continue
        if len(pending)<2:raise ValueError("Malformed postfix")
        right,left=pending.pop(),pending.pop()
        count+=1;dest=f"T{count}";op=OPS[token]
        if addresses==0:code.append((op,))
        elif addresses==1:code.extend((("LOAD",left),(op,right),("STORE",dest)))
        elif addresses==2:code.extend((("MOV",dest,left),(op,dest,right)))
        else:code.append((op,dest,left,right))
        pending.append(dest)
    if len(pending)!=1:raise ValueError("Malformed postfix")
    if addresses==0:code.append(("POP","RESULT"))
    elif addresses==1:code.extend((("LOAD",pending[0]),("STORE","RESULT")))
    else:code.append(("MOV","RESULT",pending[0]))
    return tuple(code)


def calculate(op,a,b):
    if op in ("ADD","SUB"):return alu(op,a,b).word
    if op=="MUL":return (a*b)&65535
    if op=="DIV":
        x,y=signed(a,16),signed(b,16)
        if not y:raise ValueError("Division by zero")
        q=abs(x)//abs(y)
        return (-q if (x<0)!=(y<0) else q)&65535
    raise ValueError("Invalid operation")


@dataclass(frozen=True)
class ExpressionStep:
    instruction:tuple
    accumulator:int
    stack:tuple
    writes:tuple


@dataclass(frozen=True)
class ExpressionResult:
    postfix:tuple
    program:tuple
    steps:tuple
    word:int


def evaluate_expression(source,variables,addresses):
    """Execute generated pseudo-code, each row reflects actual state changes.

    Words wrap modulo 65536; DIV interprets two's complement and truncates
    toward zero. A–D inputs are raw words. No Python eval or external code.
    """
    tokens=postfix(source)
    program=compile_expression(tokens,addresses)
    memory={key:variables.get(key,0) for key in "ABCD"}
    if any(not isinstance(v,int) or not 0<=v<=65535 for v in memory.values()):
        raise ValueError("Invalid operand word")
    stack=RegisterStack()
    ac=0;steps=[]
    def read(name):
        return int(name) if name.isdecimal() else memory[name]
    for instruction in program:
        op,*args=instruction
        writes=[]
        def store(name,value):
            memory[name]=value;writes.append((name,value))
        if op=="PUSH":stack.push(read(args[0]))
        elif op=="POP":store(args[0],stack.pop().value)
        elif op=="LOAD":ac=read(args[0])
        elif op=="STORE":store(args[0],ac)
        elif op=="MOV":store(args[0],read(args[1]))
        elif addresses==0:
            right=stack.pop().value;left=stack.pop().value
            stack.push(calculate(op,left,right))
        elif addresses==1:ac=calculate(op,ac,read(args[0]))
        elif addresses==2:store(args[0],calculate(op,read(args[0]),read(args[1])))
        else:store(args[0],calculate(op,read(args[1]),read(args[2])))
        snapshot=tuple(stack.words[i&63] for i in range(1,stack.depth+1))
        steps.append(ExpressionStep(instruction,ac,snapshot,tuple(writes)))
    return ExpressionResult(tokens,program,tuple(steps),memory["RESULT"])
