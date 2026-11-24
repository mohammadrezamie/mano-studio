"""Two-pass symbolic assembler for the separate Chapter 7 control store.

Addresses in symbolic source are decimal, or explicitly prefixed 0x hex.
The grammar is documented in docs/MICROPROGRAM.md.
"""
import re
from dataclasses import dataclass
from microprogram import Microinstruction, FIELDS, CONDITIONS, BRANCHES

OPERATIONS={name:(group,code) for group,field in enumerate(FIELDS)
            for code,name in enumerate(field) if code and name!="RESERVED"}
DESTINATIONS={
    "ADD":"AC","CLRAC":"AC","INCAC":"AC","DRTAC":"AC","DRTAR":"AR","PCTAR":"AR","WRITE":"M",
    "SUB":"AC","OR":"AC","AND":"AC","READ":"DR","ACTDR":"DR","INCDR":"DR","PCTDR":"DR",
    "XOR":"AC","COM":"AC","SHL":"AC","SHR":"AC","INCPC":"PC","ARTPC":"PC"}


@dataclass(frozen=True)
class Diagnostic:
    line:int
    code:str
    detail:str


@dataclass(frozen=True)
class MicroAssembly:
    words:dict
    labels:dict
    source_lines:dict
    errors:tuple

    @property
    def ok(self):
        return not self.errors

    def listing(self):
        if not self.ok:
            raise ValueError("Cannot list invalid microprogram")
        return "\n".join(f"{a:02X}:{w:05X}" for a,w in sorted(self.words.items()))


def address(token):
    if not re.fullmatch(r"(?:[0-9]+|0X[0-9A-F]+)",token):
        raise ValueError("ADDRESS")
    number=int(token,16 if token.startswith("0X") else 10)
    if not 0<=number<128:
        raise ValueError("ADDRESS")
    return number


def assemble_micro(source):
    labels,rows,errors={}, {}, []
    location=0
    def error(line,code,detail=""):
        errors.append(Diagnostic(line,code,detail))
    for line,raw in enumerate(source.splitlines(),1):
        text=raw.split("#",1)[0].split(";",1)[0].strip().upper()
        if not text:continue
        if ":" in text:
            label,text=(v.strip() for v in text.split(":",1))
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*",label) or label in {"NEXT","ORG"} or label in labels:
                error(line,"LABEL",label)
            elif text.split() and text.split()[0]=="ORG":
                error(line,"SYNTAX","Label cannot prefix ORG")
            elif location>=128:
                error(line,"ADDRESS",label)
            else:labels[label]=location
        if not text:continue
        if text.split()[0]=="ORG":
            try:location=address(text[3:].strip())
            except ValueError:error(line,"ADDRESS",text)
            continue
        if location>=128 or location in rows:
            error(line,"OVERLAP",str(location))
        else:rows[location]=(line,text)
        location+=1
    words={}
    for loc,(line,text) in rows.items():
        match=re.fullmatch(r"(.+?)\s+(U|I|S|Z)\s+(JMP|CALL|RET|MAP)(?:\s+(\S+))?",text)
        if not match:
            error(line,"SYNTAX",text)
            continue
        ops,cd,br,target=match.groups()
        codes=[0,0,0]
        used=set()
        destinations=set()
        valid=True
        for name in map(str.strip,ops.split(",")):
            if name=="NOP" and ops.strip()=="NOP":continue
            if name not in OPERATIONS:
                error(line,"OPERATION",name);valid=False;continue
            group,code=OPERATIONS[name]
            dest=DESTINATIONS[name]
            if group in used or dest in destinations:
                error(line,"CONFLICT",name);valid=False
            used.add(group);destinations.add(dest);codes[group]=code
        # Explicit memory-port check independent of whitespace/order.
        names={v.strip() for v in ops.split(",")}
        if {"READ","WRITE"}<=names:
            error(line,"CONFLICT","READ/WRITE");valid=False
        if br in ("RET","MAP"):
            if target not in (None,"0","0X0"):
                error(line,"TARGET",target);valid=False
            ad=0
        else:
            try:
                if target=="NEXT":ad=(loc+1)&127
                elif target in labels:ad=labels[target]
                else:ad=address(target or "")
            except ValueError:
                error(line,"TARGET",target or "");valid=False;ad=0
        if valid:
            words[loc]=Microinstruction(*codes,CONDITIONS.index(cd),BRANCHES.index(br),ad).encode()
    if not rows:error(0,"EMPTY")
    return MicroAssembly({} if errors else words,labels,
                         {loc:line for loc,(line,_) in rows.items()},tuple(errors))


# Original example using the four defined machine opcodes and a shared helper.
# Control addresses 0/4/8/12 follow the chapter's opcode mapping.
DEMO_SOURCE="""# ADD: direct or indirect
ORG 0
SUM: NOP I CALL POINTER
READ U JMP NEXT
ADD U JMP FETCH

ORG 4
NEGATIVE: NOP S JMP TAKEN
NOP U JMP FETCH
TAKEN: NOP I CALL POINTER
ARTPC U JMP FETCH

ORG 8
SAVE: NOP I CALL POINTER
ACTDR U JMP NEXT
WRITE U JMP FETCH

ORG 12
SWAP: NOP I CALL POINTER
READ U JMP NEXT
DRTAC, ACTDR U JMP NEXT
WRITE U JMP FETCH

ORG 64
FETCH: PCTAR U JMP NEXT
READ, INCPC U JMP NEXT
DRTAR U MAP

ORG 80
POINTER: READ U JMP NEXT
DRTAR U RET
"""


def full_demo():
    """Program exercises all four instructions with direct/indirect addressing."""
    result=assemble_micro(DEMO_SOURCE)
    if not result.ok:raise RuntimeError("Built-in microprogram is invalid")
    memory={0:0x0100,1:0x9101,2:0x1904,3:0x0906,
            0x100:5,0x101:0x103,0x104:0xFFFE}
    return result.words,memory
