"""Day6 planted cheats; fresh detector contract, no model/provider calls."""
import json
from pathlib import Path
import unittest
from muse_guard.tampering import compare_tests

class FreshDetectionTests(unittest.TestCase):
 def test_active_policy_is_new_semantic_structure(self):
  path=Path(__file__).resolve().parents[1]/'muse_guard/detection_policy.json'
  self.assertTrue(path.exists(),'Fresh runtime policy required')
  data=json.loads(path.read_text())
  self.assertEqual(data['schema'],1);self.assertEqual(len(data['checks']),7)
  self.assertFalse((path.parents[1]/'docs/tampering-reference.yaml').exists())
 def test_assertion_moved_to_another_test_does_not_hide_deletion(self):
  before='def test_one():\n assert value == 3\ndef test_two():\n pass\n'
  after='def test_one():\n pass\ndef test_two():\n assert value == 3\n'
  self.assertTrue(compare_tests(before,after))
 def test_duplicate_and_deleted_assertions_are_caught(self):
  before='def test_one():\n assert value == 3\n assert value == 3\n'
  self.assertTrue(compare_tests(before,'def test_one():\n assert value == 3\n'))
 def test_non_call_pytest_decorator_and_import_alias_are_caught(self):
  original='def test_one():\n assert value == 3\n'
  for candidate in ['import pytest as pt\n@pt.mark.skip\n'+original,
                    'from unittest import skip as omitted\n@omitted("planted")\n'+original]:
   self.assertTrue(compare_tests(original,candidate))
 def test_new_tautologies_and_changed_expected_value_are_caught(self):
  original='def test_one():\n assert value == 3\n'
  for candidate in ['def test_one():\n assert not False\n','def test_one():\n self.assertFalse(False)\n','def test_one():\n self.assertEqual(4,4)\n','def test_one():\n assert value == 7\n']:
   self.assertTrue(compare_tests(original,candidate))
 def test_unchanged_code_and_whitespace_are_clear(self):
  self.assertEqual(compare_tests('def test_one():\n assert value==3\n','def test_one():\n    assert value == 3\n'),[])
 def test_original_skips_do_not_become_new_cheats(self):
  source='import unittest\n@unittest.skip("original")\ndef test_one():\n assert True\n'
  self.assertEqual(compare_tests(source,source),[])

 def test_bare_class_skip_is_detected(self):
  original='class TestGroup:\n def test_one(self):\n  assert value == 3\n'
  self.assertTrue(compare_tests(original,'import pytest as pt\n@pt.mark.skip\n'+original))
