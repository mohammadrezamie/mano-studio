"""Original distinctive-shape logic symbols and pin geometry for Qt schematics."""
from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from logic_engine import valid_arity

WIDTH = 108
HEIGHT = 84
CENTER = HEIGHT / 2


def pin_offsets(count):
    if not 1 <= count <= 4:
        raise ValueError("Unsupported pin count")
    return tuple(CENTER + (i-(count-1)/2)*16 for i in range(count))


def input_point(x, y, index, count):
    return x, y + pin_offsets(count)[index]


def output_point(x, y):
    return x + WIDTH, y + CENTER


def draw_gate(scene, op, x, y, bits, output, palette):
    """Draw actual pins and distinctive shapes. No invented package pin numbers."""
    if not valid_arity(op, len(bits)):
        raise ValueError("Invalid gate symbol arity")
    bg,panel,raised,fg,muted,accent,border = palette
    invert = op in ("NOT","NAND","NOR","XNOR")
    color = lambda bit: QColor(accent if bit else muted)
    def path(points, pen, brush=None):
        return scene.addPath(points, pen, brush if brush is not None else QBrush())
    def line(x1,y1,x2,y2,bit):
        scene.addLine(x+x1,y+y1,x+x2,y+y2,QPen(color(bit),1.8 if bit else 1.1))
    # Stubs run under the opaque body to meet its exact outline.
    for offset,bit in zip(pin_offsets(len(bits)),bits):
        line(0,offset,48,offset,bit)
    line(75,CENTER,WIDTH,CENTER,output)
    body=QPainterPath()
    if op == "NOT":
        body.moveTo(x+25,y+9)
        body.lineTo(x+75,y+CENTER)
        body.lineTo(x+25,y+75)
    elif op in ("AND","NAND"):
        body.moveTo(x+25,y+7)
        body.lineTo(x+46,y+7)
        body.cubicTo(x+85,y+7,x+85,y+77,x+46,y+77)
        body.lineTo(x+25,y+77)
    else:
        body.moveTo(x+22,y+7)
        body.cubicTo(x+49,y+7,x+64,y+18,x+82,y+CENTER)
        body.cubicTo(x+64,y+66,x+49,y+77,x+22,y+77)
        body.cubicTo(x+42,y+55,x+42,y+29,x+22,y+7)
    body.closeSubpath()
    path(body,QPen(QColor(fg),1.6),QBrush(QColor(panel)))
    if op in ("XOR","XNOR"):
        extra=QPainterPath()
        extra.moveTo(x+14,y+7)
        extra.cubicTo(x+34,y+29,x+34,y+55,x+14,y+77)
        path(extra,QPen(QColor(fg),1.6))
    # AND body's Bezier apex is x+75.25; OR is x+82; NOT x+75.
    tip=82 if op in ("NOR","XNOR") else 75
    if invert:
        scene.addEllipse(QRectF(x+tip,y+CENTER-4.5,9,9),QPen(QColor(fg),1.6),QBrush(QColor(bg)))
    # Terminals are signal anchors, distinct from inversion bubbles.
    for offset,bit in zip(pin_offsets(len(bits)),bits):
        scene.addEllipse(QRectF(x-2,y+offset-2,4,4),QPen(color(bit),1),QBrush(color(bit)))
    scene.addEllipse(QRectF(x+WIDTH-2,y+CENTER-2,4,4),QPen(color(output),1),QBrush(color(output)))
