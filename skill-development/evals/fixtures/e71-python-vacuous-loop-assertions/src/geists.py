def suggest(notes, min_links=2):
    """Return a suggestion for every note with at least `min_links` outgoing links."""
    out = []
    for note in notes:
        links = note.get("links", [])
        if len(links) >= min_links:
            out.append(f"Revisit {note['title']}: it connects {len(links)} ideas")
    return out
