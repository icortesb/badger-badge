BASE = (
    ("GitHub", "github.com/icortesb", "https://github.com/icortesb"),
    ("LinkedIn", "in/ivan-cortes-buenard", "https://www.linkedin.com/in/ivan-cortes-buenard/"),
    ("dishape.dev", "dishape.dev", "https://dishape.dev"),
)


def vcard(contact):
    first = contact.get("first", "")
    last = contact.get("last", "")
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:{};{}".format(last, first), "FN:{} {}".format(first, last)]
    if contact.get("email"):
        lines.append("EMAIL:" + contact["email"])
    if contact.get("phone"):
        lines.append("TEL:" + contact["phone"])
    lines.append("END:VCARD")
    return "\r\n".join(lines)


def items(contact):
    result = [{"label": label, "text": text, "payload": payload} for label, text, payload in BASE]
    if contact and contact.get("first"):
        result.append({"label": "Contacto", "text": "Guardá mi contacto", "payload": vcard(contact)})
    return result
