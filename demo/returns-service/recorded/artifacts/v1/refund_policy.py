"""Baseline policy. Next actions are simulated; no payment is made."""
def next_action(request):
    if request['eligible']:
        return 'refund_immediately'
    return 'reject'
