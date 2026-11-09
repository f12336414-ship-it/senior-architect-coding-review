class Ticket:
    def __init__(self, title):
        if not title.strip():
            raise ValueError("title required")
        self.title = title
        self.state = "draft"

    def transition(self, target):
        raise NotImplementedError
