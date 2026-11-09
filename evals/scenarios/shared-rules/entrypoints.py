def cli_transition(ticket, target):
    ticket.transition(target)
    return ticket.state


def http_transition(ticket, target):
    ticket.transition(target)
    return {"title": ticket.title, "state": ticket.state}
