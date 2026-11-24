from learning_catalog import CHAPTERS,TOOLS,BY_ID,search_tools,clean_progress


def test_catalog_stable_and_complete_index():
    assert [c.number for c in CHAPTERS]==list(range(1,14))
    assert len(TOOLS)==len(BY_ID)==34
    assert all(t.title[0] and t.title[1] and t.task[0] and t.task[1] for t in TOOLS)
    assert all(c.gap[0] and c.gap[1] for c in CHAPTERS)
    assert [t.id for t in search_tools(chapter=13)]==['multiprocessor']
    assert {t.chapter for t in TOOLS}==set(range(1,14))


def test_search_and_explicit_progress():
    assert search_tools("dma",11)[0].id=="dma"
    assert any(t.id=="codes" for t in search_tools("كدهاي داده"))
    assert search_tools("pipeline",9)
    assert all(t.chapter==9 for t in search_tools("pipeline",9))
    assert not search_tools("dma",11,("dma",),True)
    assert clean_progress(["dma","dma","unknown",None])==("dma",)
