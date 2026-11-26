from html.parser import HTMLParser
from instructor_evidence import expected_captures
from instructor_gallery import write_gallery


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs['src'])
        elif tag == 'a':
            self.links.append(attrs['href'])


def test_gallery_contains_every_local_capture_once(tmp_path):
    expected = expected_captures()
    rows = [{'image': name, 'width': (size or (500, 300))[0],
             'height': (size or (500, 300))[1]} for name, size in expected.items()]
    page = write_gallery(tmp_path, rows).read_text(encoding='utf-8')
    parser = Links()
    parser.feed(page)
    assert len(parser.images) == 36
    assert set(parser.images) == set(expected)
    assert set(expected).issubset(parser.links)
    assert all(not link.startswith(('http:', 'https:', '//')) for link in parser.links)
    assert 'lang="fa" dir="rtl"' in page
    assert 'Native Windows acceptance remains separate' in page
