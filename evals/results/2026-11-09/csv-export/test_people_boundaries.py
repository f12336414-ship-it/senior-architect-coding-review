import csv
import io
import unittest

from exports import export_people


class PeopleBoundaryTests(unittest.TestCase):
    def test_special_values_in_both_fields_preserved(self):
        values = ["", " a ", "A,B", 'Say "yes"', "a\rb", "a\nb", "a\r\nb", "张三🌟", "=1+1"]
        for value in values:
            with self.subTest(value=value):
                person = {"name": value, "email": value}
                result = export_people(iter([person]))
                rows = list(csv.reader(io.StringIO(result, newline="")))
                self.assertEqual(rows, [["name", "email"], [value, value]])
                self.assertEqual(person, {"name": value, "email": value})

    def test_exact_escaping_and_record_terminator(self):
        actual = export_people([{"name": 'A,"B"', "email": "first\nsecond"}])
        self.assertEqual(actual, 'name,email\r\n"A,""B""","first\nsecond"\r\n')

    def test_empty_one_shot_iterator(self):
        self.assertEqual(export_people(iter(())), "name,email\r\n")


if __name__ == "__main__":
    unittest.main()
