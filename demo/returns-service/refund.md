Returns service refund policy change

The service must choose exactly ONE next action for each stored return.
The only policy inputs are eligible and fraud_hold, each true or false.
The action names used by this service are refund_immediately, manual_review and reject.

For every eligible request, refund immediately.
For every request on fraud hold, do not refund until manual review.
If neither rule matches, reject the refund.
