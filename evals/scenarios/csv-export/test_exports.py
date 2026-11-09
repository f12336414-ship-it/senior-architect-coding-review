import csv
import io
import unittest

from exports import export_people, export_projects


class ExportTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(export_people([]), "name,email\r\n")

    def test_simple(self):
        self.assertEqual(export_people([{"name": "Ada", "email": "a@example.test"}]),
                         "name,email\r\nAda,a@example.test\r\n")

    def test_special_fields_round_trip(self):
        names = ['A,B', 'Say "yes"', "line\r\nbreak", "张三", " spaced ", ""]
        people = [{"name": name, "email": "a@example.test"} for name in names]
        actual = list(csv.reader(io.StringIO(export_people(people), newline="")))
        self.assertEqual(actual, [["name", "email"]] + [[p["name"], p["email"]] for p in people])

    def test_one_shot_iterator(self):
        people = ({"name": str(i), "email": "x"} for i in range(3))
        self.assertEqual(export_people(people), "name,email\r\n0,x\r\n1,x\r\n2,x\r\n")

    def test_existing_export(self):
        self.assertEqual(export_projects([{"id": 1, "name": "A,B"}]), 'id,name\r\n1,"A,B"\r\n')


if __name__ == "__main__":
    unittest.main()
