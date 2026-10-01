def suggest(notes, min_links=2):
    """Mutant: threshold typo silently suppresses every suggestion."""
    out = []
    for note in notes:
        links = note.get("links", [])
        if len(links) >= min_links * 10:
            out.append(f"Revisit {note['title']}: it connects {len(links)} ideas")
    return out
