class Ticket:
    def __init__(self, title):
        if not title.strip():
            raise ValueError("title required")
        self.title = title
        self.state = "draft"

    def transition(self, target):
        transitions = {
            "draft": ("in_review",),
            "in_review": ("draft", "approved"),
            "approved": ("published",),
            "published": (),
        }
        if not isinstance(target, str) or target not in transitions:
            raise ValueError("unknown state")
        if target == self.state:
            return
        if target not in transitions.get(self.state, ()):
            raise ValueError("invalid state transition")
        self.state = target
