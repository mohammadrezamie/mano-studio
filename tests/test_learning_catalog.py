from learning_catalog import CHAPTERS,TOOLS,BY_ID,search_tools,clean_progress


def test_catalog_stable_and_complete_index():
    assert [c.number for c in CHAPTERS]==list(range(1,14))
    assert len(TOOLS)==len(BY_ID)==44
    assert all(t.title[0] and t.title[1] and t.task[0] and t.task[1] for t in TOOLS)
    assert all(c.gap[0] and c.gap[1] for c in CHAPTERS)
    assert [t.id for t in search_tools(chapter=13)]==['multiprocessor','crossbar','synchronization','coherence','omega']
    assert {t.chapter for t in TOOLS}==set(range(1,14))


def test_search_and_explicit_progress():
    assert search_tools("dma",11)[0].id=="dma"
    assert any(t.id=="codes" for t in search_tools("كدهاي داده"))
    assert search_tools("pipeline",9)
    assert all(t.chapter==9 for t in search_tools("pipeline",9))
    assert not search_tools("dma",11,("dma",),True)
    assert clean_progress(["dma","dma","unknown",None])==("dma",)


def test_karnaugh_search():
    assert any(t.id=="karnaugh" for t in search_tools("کارنو",1))
    assert BY_ID["karnaugh"].route=="karnaugh"


def test_coherence_search():
    assert BY_ID["coherence"].route == "coherence"
    assert any(t.id == "coherence" for t in search_tools("BusRdX",13))
    assert any(t.id == "coherence" for t in search_tools("هماهنگی کش",13))


def test_omega_search():
    assert BY_ID["omega"].route == "omega"
    assert any(t.id=="omega" for t in search_tools("perfect shuffle",13))
    assert any(t.id=="omega" for t in search_tools("امگا",13))


def test_boolean_law_search():
    for query in ("De Morgan","duality","دمورگان","دوگانگی"):
        assert any(t.id=="karnaugh" for t in search_tools(query,1))


def test_flipflop_reference_search():
    for query in ("excitation","characteristic","تحریک","مشخصه"):
        assert any(t.id=="sequential" for t in search_tools(query,1))
