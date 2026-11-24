"""Functional content-addressable memory; mask bit 1 means compare."""
from dataclasses import dataclass


def checked_word(value,width):
    if type(value) is not int or not 0<=value<(1<<width):
        raise ValueError("Word outside width")
    return value


def masked_match(word,key,mask,width=8):
    for value in (word,key,mask):checked_word(value,width)
    return ((word^key)&mask)==0


@dataclass(frozen=True)
class Match:
    matches:tuple
    first:int | None


class AssociativeMemory:
    def __init__(self):
        self.words=[None]*8

    def write(self,row,word):
        if type(row) is not int or not 0<=row<8:raise ValueError("Invalid row")
        self.words[row]=checked_word(word,8)

    def invalidate(self,row):
        if type(row) is not int or not 0<=row<8:raise ValueError("Invalid row")
        self.words[row]=None

    def search(self,key,mask=255):
        checked_word(key,8);checked_word(mask,8)
        matches=tuple(i for i,word in enumerate(self.words)
                      if word is not None and masked_match(word,key,mask))
        return Match(matches,matches[0] if matches else None)
