from ui.theme import PALETTES,SPACING,RADIUS,TYPE,stylesheet


def luminance(color):
    rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in rgb]
    return sum(v*w for v,w in zip(linear,(.2126,.7152,.0722)))


def contrast(a,b):
    x,y=sorted((luminance(a),luminance(b)))
    return (y+.05)/(x+.05)


def test_text_contrast_tokens():
    for name,(bg,panel,raised,fg,muted,accent,border) in PALETTES.items():
        for surface in (bg,panel,raised):
            assert contrast(fg,surface)>=4.5
            assert contrast(muted,surface)>=4.5
        assert contrast(accent,raised)>=4.5
        assert contrast("#ffffff" if name=="light" else bg,accent)>=4.5


def test_design_token_order_and_plain_fallback():
    assert SPACING==tuple(sorted(set(SPACING)))
    assert RADIUS["control"]<RADIUS["panel"]<RADIUS["shell"]
    assert TYPE["caption"]<TYPE["body"]<TYPE["section"]<TYPE["title"]<TYPE["hero"]
    for theme in PALETTES:
        assert "qlineargradient" in stylesheet(theme,True)
        assert "qlineargradient" not in stylesheet(theme,False)
