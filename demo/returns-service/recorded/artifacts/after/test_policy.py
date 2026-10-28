import unittest
from refund_policy import next_action
class ApprovedPolicy(unittest.TestCase):
 def test_eligible_fraud_held(self):self.assertEqual(next_action({'eligible': True, 'fraud_hold': True}), 'manual_review')
 def test_eligible_not_held(self):self.assertEqual(next_action({'eligible': True, 'fraud_hold': False}), 'refund_immediately')
 def test_ineligible_not_held(self):self.assertEqual(next_action({'eligible': False, 'fraud_hold': False}), 'reject')
