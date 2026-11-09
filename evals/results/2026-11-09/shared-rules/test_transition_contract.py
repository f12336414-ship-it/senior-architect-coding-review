import unittest

from entrypoints import cli_transition, http_transition
from tickets import Ticket


class TransitionContractTests(unittest.TestCase):
    def test_shared_instance_round_trip_and_return_values(self):
        ticket = Ticket("Article")
        for target in ("in_review", "draft", "in_review", "approved", "published"):
            with self.subTest(target=target):
                self.assertEqual(cli_transition(ticket, target), target)
                self.assertEqual(
                    http_transition(ticket, target),
                    {"title": "Article", "state": target},
                )
                self.assertIsNone(ticket.transition(target))

    def test_direct_transition_returns_none(self):
        ticket = Ticket("Article")
        self.assertIsNone(ticket.transition("in_review"))
        self.assertEqual(ticket.state, "in_review")

    def test_unknown_targets_preserve_entire_ticket(self):
        for source in ("draft", "in_review", "approved", "published"):
            for target in ("", "unknown", "Draft", None, 1, [], {}):
                for entry in (Ticket.transition, cli_transition, http_transition):
                    with self.subTest(source=source, target=target, entry=entry.__name__):
                        ticket = Ticket("Article")
                        ticket.state = source
                        before = vars(ticket).copy()
                        with self.assertRaises(ValueError):
                            entry(ticket, target)
                        self.assertEqual(vars(ticket), before)

    def test_constructor_contract_is_unchanged(self):
        for title in ("", "  "):
            with self.subTest(title=title), self.assertRaises(ValueError):
                Ticket(title)
        ticket = Ticket(" Article ")
        self.assertEqual((ticket.title, ticket.state), (" Article ", "draft"))


if __name__ == "__main__":
    unittest.main()
