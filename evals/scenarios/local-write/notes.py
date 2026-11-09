"""Local notebook operations; callers own the SQLite connection and transaction."""


def get_note(connection, note_id):
    row = connection.execute(
        "SELECT id, title FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    if row is None:
        raise KeyError(note_id)
    return {"id": row[0], "title": row[1]}


def rename_note(connection, note_id, title):
    raise NotImplementedError
