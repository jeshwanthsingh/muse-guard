"""Approved next action; simulated only, never a payment."""
def next_action(request):
    if request["fraud_hold"]:
        return "manual_review"
    if request["eligible"]:
        return "refund_immediately"
    return "reject"
