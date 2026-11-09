def submit_payment(gateway, order_id, amount):
    return gateway.charge(order_id=order_id, amount=amount)
