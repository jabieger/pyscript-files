from pyscript.web import page, a

def links_hinzufuegen_zu(target):  # target ist die id des Ziel-divs
    div = page[target]

    div.append(
        a(
            "Wikipedia",
            href="https://de.wikipedia.org",
            target="_blank"
        )
    )

    div.append(
        a(
            "YouTube",
            href="https://www.youtube.com",
            target="_blank"
        )
    )

def check():
    return "Einbindung erfolgreich: sources.py"
