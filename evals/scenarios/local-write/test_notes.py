import sqlite3
import unittest

from notes import get_note, rename_note


class RenameTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
        self.connection.executemany("INSERT INTO notes VALUES (?, ?)", [(1, "old"), (2, "other")])
        self.connection.commit()

    def test_rename_and_preserve_other_record(self):
        self.assertEqual(rename_note(self.connection, 1, " new "), {"id": 1, "title": "new"})
        self.assertEqual(get_note(self.connection, 2)["title"], "other")

    def test_invalid_title_does_not_write(self):
        for title in (None, 3, "", " \t\n"):
            with self.subTest(title=title), self.assertRaises(ValueError):
                rename_note(self.connection, 1, title)
        self.assertEqual(get_note(self.connection, 1)["title"], "old")

    def test_missing_record(self):
        with self.assertRaises(KeyError):
            rename_note(self.connection, 99, "valid")
        self.assertEqual(get_note(self.connection, 1)["title"], "old")

    def test_quote_is_data(self):
        value = "O'Reilly; DROP TABLE notes; --"
        self.assertEqual(rename_note(self.connection, 1, value)["title"], value)
        self.assertEqual(get_note(self.connection, 2)["title"], "other")

    def test_caller_can_rollback(self):
        rename_note(self.connection, 1, "changed")
        self.connection.rollback()
        self.assertEqual(get_note(self.connection, 1)["title"], "old")

    def test_failure_does_not_rollback_caller_work(self):
        self.connection.execute("UPDATE notes SET title = 'pending' WHERE id = 2")
        with self.assertRaises(ValueError):
            rename_note(self.connection, 1, " ")
        self.assertEqual(get_note(self.connection, 2)["title"], "pending")


if __name__ == "__main__":
    unittest.main()
