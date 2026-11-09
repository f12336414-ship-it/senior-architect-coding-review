"""Local notebook operations; callers own the SQLite connection and transaction."""


def get_note(connection, note_id):
    row = connection.execute(
        "SELECT id, title FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    if row is None:
        raise KeyError(note_id)
    return {"id": row[0], "title": row[1]}


def rename_note(connection, note_id, title):
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    connection.execute(
        "UPDATE notes SET title = ? WHERE id = ?", (title.strip(), note_id)
    )
    return get_note(connection, note_id)
