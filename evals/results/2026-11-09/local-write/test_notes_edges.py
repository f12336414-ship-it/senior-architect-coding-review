import sqlite3
import unittest

from notes import get_note, rename_note


class RenameEdgeTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.execute(
            "CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)"
        )
        self.connection.executemany(
            "INSERT INTO notes VALUES (?, ?)", [(1, "old"), (2, "other")]
        )
        self.connection.commit()

    def test_same_title_is_not_missing(self):
        self.assertEqual(
            rename_note(self.connection, 1, "old"), {"id": 1, "title": "old"}
        )

    def test_trim_unicode_edges_preserves_internal_space(self):
        self.assertEqual(
            rename_note(self.connection, 1, "\u3000hello  world\u00a0"),
            {"id": 1, "title": "hello  world"},
        )

    def test_success_keeps_caller_work_uncommitted(self):
        self.connection.execute("UPDATE notes SET title = 'pending' WHERE id = 2")
        rename_note(self.connection, 1, "changed")
        self.assertEqual(get_note(self.connection, 2)["title"], "pending")
        self.connection.rollback()
        self.assertEqual(get_note(self.connection, 1)["title"], "old")
        self.assertEqual(get_note(self.connection, 2)["title"], "other")

    def test_missing_keeps_caller_work_uncommitted(self):
        self.connection.execute("UPDATE notes SET title = 'pending' WHERE id = 2")
        with self.assertRaises(KeyError) as error:
            rename_note(self.connection, 99, "valid")
        self.assertEqual(error.exception.args, (99,))
        self.assertEqual(get_note(self.connection, 2)["title"], "pending")
        self.connection.rollback()
        self.assertEqual(get_note(self.connection, 2)["title"], "other")

    def test_database_error_preserves_caller_work(self):
        self.connection.execute("UPDATE notes SET title = 'pending' WHERE id = 2")

        def deny_update(action, *args):
            return sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_UPDATE else sqlite3.SQLITE_OK

        self.connection.set_authorizer(deny_update)
        try:
            with self.assertRaises(sqlite3.DatabaseError):
                rename_note(self.connection, 1, "changed")
        finally:
            self.connection.set_authorizer(None)
        self.assertEqual(get_note(self.connection, 1)["title"], "old")
        self.assertEqual(get_note(self.connection, 2)["title"], "pending")
        self.connection.rollback()
        self.assertEqual(get_note(self.connection, 2)["title"], "other")
