"""Chapter 11 ideal asynchronous handshake and priority interrupt models.

No real-time clock, electrical timing, metastability or commercial PIC.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class HandshakeEvent:
    number:int
    action:str
    valid:bool
    ready:bool
    bus:int | None
    received:int | None


class Handshake:
    """Four ordered signal transitions; source drives bus/valid, destination ready.

    Source initiated: valid↑, ready↑/capture, valid↓, ready↓.
    Destination initiated: ready↑, valid↑, ready↓/capture, valid↓.
    Each action models one asynchronous event, not one fixed clock.
    """
    SEQUENCES={
        "source":("offer","accept","release_data","release_ready"),
        "destination":("request","provide","receive","release_data")}

    def __init__(self,mode="source"):
        if mode not in self.SEQUENCES:raise ValueError("Invalid handshake mode")
        self.mode=mode
        self.phase=0
        self.valid=False
        self.ready=False
        self.bus=None
        self.received=[]
        self.events=[]

    @property
    def next_action(self):return self.SEQUENCES[self.mode][self.phase]

    def act(self,action,value=None):
        if action!=self.next_action:raise ValueError("Out-of-order handshake")
        if action in ("offer","provide"):
            if type(value) is not int or not 0<=value<256:
                raise ValueError("Invalid data byte")
        elif value is not None:raise ValueError("Unexpected data")
        captured=None
        if action in ("offer","provide"):
            self.bus=value
            self.valid=True
        elif action=="request":self.ready=True
        elif action in ("accept","receive"):
            captured=self.bus
            self.received.append(captured)
            self.ready=action=="accept"
        elif action=="release_data":
            self.valid=False
            self.bus=None
        elif action=="release_ready":self.ready=False
        self.phase=(self.phase+1)%4
        event=HandshakeEvent(len(self.events)+1,action,self.valid,self.ready,self.bus,captured)
        self.events.append(event)
        return event


@dataclass(frozen=True)
class InterruptSelection:
    pending:int
    mask:int
    eligible:int
    winner:int | None
    vector:int | None
    grant:tuple


class PriorityInterrupt:
    """Four latched request bits, bit 0 highest, mask bit 1 enables.

    Acknowledge clears the selected request and pushes its service level.
    Higher-priority nesting is allowed while globally enabled; EOI pops
    exactly the current service level. Repeated requests coalesce per bit.
    Vector 0100 + 4*i is an explicitly chosen example address.
    """
    def __init__(self):
        self.pending=0
        self.mask=15
        self.enabled=True
        self.service=[]

    def request(self,device):
        if type(device) is not int or not 0<=device<4:
            raise ValueError("Invalid device")
        self.pending|=1<<device

    def set_mask(self,mask):
        if type(mask) is not int or not 0<=mask<16:
            raise ValueError("Invalid mask")
        self.mask=mask

    def select(self):
        limit=(1<<self.service[-1])-1 if self.service else 15
        eligible=self.pending & self.mask & limit if self.enabled else 0
        winner=None
        grant_in=bool(eligible)
        grant=[]
        for i in range(4):
            accepted=grant_in and bool(eligible & (1<<i))
            grant_out=grant_in and not accepted
            grant.append((i,grant_in,accepted,grant_out))
            if accepted:winner=i
            grant_in=grant_out
        return InterruptSelection(self.pending,self.mask,eligible,winner,
                                  None if winner is None else 0x100+4*winner,tuple(grant))

    def acknowledge(self):
        result=self.select()
        if result.winner is None:raise ValueError("No eligible interrupt")
        self.pending&=~(1<<result.winner)
        self.service.append(result.winner)
        return result

    def end(self):
        if not self.service:raise ValueError("No interrupt in service")
        return self.service.pop()
