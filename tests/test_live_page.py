import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from live_demo.app import create_app
class LivePageRenderTests(unittest.TestCase):
 def setUp(self):
  self.client=TestClient(create_app(None,{},mode='test'))
  self.html=self.client.get('/').text
 def test_landing_section_renders(self):
  for text in ('Resolve the policy. Check the code.','When requirements clash, muse-guard shows exactly where',
               'Try the example (60 seconds)','See it change real code','Built with Muse Spark + Muse Code',
               'Meta Global AI Developer Hackathon 2026','Requirements','Clash found','You decide','Checked code'):
   self.assertIn(text,self.html)
 def test_results_strip_uses_only_measured_numbers(self):
  for text in ('160','0/77','39/40 → 40/40','about +2%','+9% coding steps','null result'):
   self.assertIn(text,self.html)
  self.assertNotIn('79/80',self.html)
 def test_real_run_section_matches_run_record(self):
  for text in ('refund_immediately','manual_review','4/4 policy cases','7/7 existing regressions',
               'the record marks that as a test edit','/recorded/returns-run/index.html'):
   self.assertIn(text,self.html)
 def test_honesty_text_kept(self):
  for text in ('Live:','requirements check only','What this does NOT check','checked over declared inputs','It is not a proof.'):
   self.assertIn(text,self.html)
 def test_social_card_and_meta_tags(self):
  for text in ('property="og:image"','/assets/og.png','name="twitter:card" content="summary_large_image"','name="description"'):
   self.assertIn(text,self.html)
  self.assertIn('rel="icon" href="/assets/favicon.svg"',self.html)
 def test_social_image_served_and_csp_unchanged(self):
  r=self.client.get('/assets/og.png')
  self.assertEqual(r.status_code,200);self.assertEqual(r.headers['content-type'],'image/png')
  self.assertIn("default-src 'none'",self.client.get('/').headers['content-security-policy'])
 def test_csp_allows_only_same_origin_images(self):
  csp=self.client.get('/').headers['content-security-policy']
  d={x.split(' ')[0]:x.split(' ',1)[1] if ' ' in x else '' for x in (p.strip() for p in csp.split(';')) if x}
  self.assertEqual(d['default-src'],"'none'");self.assertEqual(d['img-src'],"'self'")
  self.assertEqual(d['script-src'],"'unsafe-inline'");self.assertEqual(d['style-src'],"'unsafe-inline'")
  self.assertNotIn('data:',csp);self.assertNotIn('http',csp)
  self.assertEqual(self.client.get('/assets/favicon.svg').headers['content-type'],'image/svg+xml')
 def test_banner_is_one_live_line_and_links_moved(self):
  import re
  banner=re.search(r'<div class="banner".*?</div>',self.html,re.S).group(0)
  self.assertIn('requirements check only',banner);self.assertNotIn('/recorded/',banner)
  footer=re.search(r'<footer.*?</footer>',self.html,re.S).group(0)
  self.assertIn('Earlier returns demo (fake responses)',footer);self.assertIn('/recorded/index.html',footer)
 def test_rule_states_and_changed_values_are_labelled(self):
  for text in ("'Confirmed'","'Rejected'","' confirmed'","' rejected'","'primary'","<mark>refund_immediately</mark>","<mark>manual_review</mark>"):
   self.assertIn(text,self.html)
 def test_try_button_and_recorded_links_wired(self):
  for text in ("$('try').addEventListener","$('review').scrollIntoView",'/recorded/recorded-runs/index.html','/recorded/index.html'):
   self.assertIn(text,self.html)
if __name__=='__main__':unittest.main()
