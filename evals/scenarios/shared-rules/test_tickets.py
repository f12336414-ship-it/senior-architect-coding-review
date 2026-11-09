import unittest

from entrypoints import cli_transition, http_transition
from tickets import Ticket


class TransitionTests(unittest.TestCase):
    def test_both_entries_share_rules(self):
        ticket = Ticket("Design")
        self.assertEqual(cli_transition(ticket, "in_review"), "in_review")
        self.assertEqual(http_transition(ticket, "approved"), {"title": "Design", "state": "approved"})
        self.assertEqual(cli_transition(ticket, "published"), "published")

    def test_all_state_pairs(self):
        states = ("draft", "in_review", "approved", "published")
        allowed = {("draft", "in_review"), ("in_review", "draft"),
                   ("in_review", "approved"), ("approved", "published")}
        for source in states:
            for target in states + ("unknown",):
                for entry in (cli_transition, http_transition):
                    with self.subTest(source=source, target=target, entry=entry.__name__):
                        ticket = Ticket("Test")
                        ticket.state = source
                        if source == target or (source, target) in allowed:
                            entry(ticket, target)
                            self.assertEqual(ticket.state, target)
                        else:
                            with self.assertRaises(ValueError):
                                entry(ticket, target)
                            self.assertEqual(ticket.state, source)

    def test_rejection_then_valid_transition(self):
        ticket = Ticket("Test")
        with self.assertRaises(ValueError):
            http_transition(ticket, "published")
        self.assertEqual(cli_transition(ticket, "in_review"), "in_review")


if __name__ == "__main__":
    unittest.main()
