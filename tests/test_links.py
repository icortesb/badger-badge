import links
import projects

CONTACT = {"first": "Ivan", "last": "Cortes", "email": "dishape.dev@gmail.com", "phone": "+5491100000000"}


def test_items_without_contact():
    items = links.items({})
    assert [i["label"] for i in items] == ["GitHub", "LinkedIn", "dishape.dev"]
    assert items[0]["payload"] == "https://github.com/icortesb"


def test_items_with_contact_add_vcard():
    items = links.items(CONTACT)
    assert items[-1]["label"] == "Contacto"
    assert items[-1]["payload"] == links.vcard(CONTACT)


def test_vcard_format():
    card = links.vcard(CONTACT)
    lines = card.split("\r\n")
    assert lines[0] == "BEGIN:VCARD" and lines[-1] == "END:VCARD"
    assert "FN:Ivan Cortes" in lines
    assert "EMAIL:dishape.dev@gmail.com" in lines
    assert "TEL:+5491100000000" in lines


def test_vcard_is_small_enough_for_the_qr():
    assert len(links.vcard(CONTACT)) <= 160


def test_vcard_skips_missing_fields():
    card = links.vcard({"first": "Ivan", "last": "Cortes"})
    assert "TEL" not in card and "EMAIL" not in card


def test_item_texts_fit_next_to_qr():
    for item in links.items(CONTACT):
        assert len(item["label"]) <= 14
        assert len(item["text"]) <= 28


def test_project_lines_fit_the_screen():
    assert [p["name"] for p in projects.PROJECTS] == ["cupstui", "lazykuma"]
    for p in projects.PROJECTS:
        assert len(p["lines"]) <= 10
        for line in p["lines"]:
            assert len(line) <= 46, line
            assert "¿" not in line and all(ord(c) < 256 for c in line)
