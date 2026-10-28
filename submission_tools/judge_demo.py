"""Measured results and a local rule playground; frozen evidence is never edited."""
import copy
import json
from pathlib import Path
from html import escape
from muse_guard.rules import PAIRS

ASSETS = Path(__file__).with_name('judge_assets')


def demo_tables():
    tables = []
    for pair, title in [('refund', 'Refund policy'), ('retry', 'HTTP retry policy')]:
        for kind in ('impossible', 'solvable'):
            req = copy.deepcopy(PAIRS[pair][kind])
            req['title'] = title + (' — conflicting rules' if kind == 'impossible' else ' — normal task')
            tables.append(req)
    return tables


RESULTS = """<section class="results-card" aria-labelledby="study-heading">
<h2 id="study-heading">What the completed study found</h2>
<p>160 runs = 20 locked task pairs × 2 twins × 2 repeats × 2 modes; not 160 independent problems</p>
<div class="result-numbers"><div><strong>0 / 0 / 0</strong><span>Contradicted claims / test edits / visible-pass, hidden-fail repairs in either mode</span></div><div><strong>39/40 → 40/40</strong><span>Recovery after one decision: plain → guarded</span></div><div><strong>+2% cost · +9% steps</strong><span>Observed guarded overhead, including clash explanations in cost</span></div></div>
<p>Per mode: <b>80 initial attempts + 40 repairs</b>. Explicit completion claims: plain <b>40 initial + 37 repair = 77</b>; guarded <b>37 initial + 40 repair = 77</b>. Contradicted claims: <b>0/77 claiming attempts in each mode</b> (also 0/120 total coding attempts).</p>
<p><b>The one-flow recovery difference is not a proven advantage.</b> Both modes passed all 40 solvable runs. Old rule files still contradicted the decision in the plain refusal; refusing was reasonable. Guarded mode keeps instructions synchronized. This was not dishonesty.</p>
<p><b>Spec extraction: strict 7/10 docs.</b> Original set: 6/8; all 5 clashes found, 0 false. Separate Claude-written, user-reviewed set: 1/2. Doc1 recognized four clashes in its own representation but failed the fixed Boolean/field/action matching rubric; it remains a failure. <a href="extraction-failures.html">Why the three extractions failed →</a></p>
<p class="scope">Two earlier cohorts were excluded for harness stops: the first on reminder-session export policy, the second on a repository-root/accounting bug; their $0.32629155 cost remains in the $15.76510530 study total.</p>
<p class="scope">Scope: small finite rule tables, 20 holdout pairs, Muse Code 1.4.2 with Muse Spark 1.3. These results do not establish performance on arbitrary software. <a href="results.html">Read counts, costs and limitations →</a></p>
</section>"""

PLAYGROUND = """<section class="playground" aria-labelledby="playground-heading">
<h2 id="playground-heading">Try it: change the rules, preview the decision</h2>
<p>Interactive example · browser only. Toggle rules or edit actions to compare A wins with B wins.</p>
<label for="demo-table">Rule table</label><select id="demo-table"></select><button id="reset-rules" type="button">Reset this table</button>
<details class="input-details"><summary>Declared inputs and action meanings</summary><p id="declared-fields" class="boundary"></p><p class="boundary">Choose ONE next action per input. refund = refund immediately; manual_review = do not refund until review. retry = retry now; stop = do not retry.</p></details>
<table><caption class="boundary">Conditions and input domains stay fixed; enabled rules and actions are editable.</caption><thead><tr><th scope="col">On / rule</th><th scope="col">Condition</th><th scope="col">Next action</th></tr></thead><tbody id="rule-rows"></tbody></table>
<p id="clash-status" role="status" aria-live="polite"></p><div id="clash-cards" class="clash-cards"></div>
<p class="boundary">What this does NOT check: whether English was translated correctly, omitted requirements, undeclared inputs, or running code. Edits are temporary and never change recorded runs.</p>
<noscript>Enable JavaScript to use this local example. Recorded evidence remains available below.</noscript>
</section>"""


def install(out, report):
    out = Path(out)
    page = (out/'index.html').read_text()
    page = page.replace("style-src 'self' file:;", "style-src 'self' file:; script-src 'self' file:;")
    page = page.replace('</head>', '<link rel="stylesheet" href="editor.css"><script defer src="clashes.js"></script><script defer src="tables.js"></script><script defer src="editor.js"></script></head>')
    page = page.replace('<main>', '<main>'+RESULTS, 1)
    page = page.replace('Historical development examples, not a completed study.', 'These recorded development examples are separate from the completed study above.')
    page = page.replace('<div class="run-grid">', PLAYGROUND+'<h2 class="recordings-title">Recorded runs</h2><div class="run-grid">')
    page = page.replace('Read-only demo · Opens offline · No live model calls', 'Local rule playground + read-only recordings · Opens offline · No model calls')
    (out/'index.html').write_text(page)
    for name in ('clashes.js', 'editor.js', 'editor.css'):
        (out/name).write_bytes((ASSETS/name).read_bytes())
    (out/'tables.js').write_text('globalThis.MuseGuardDemoTables = '+json.dumps(demo_tables(),allow_nan=False)+';\n')
    # Plain text is HTML-escaped; no Markdown execution or raw session data.
    (out/'results.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' file:; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>Measured results — muse-guard</title><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="editor.css"></head><body><header><a href="index.html">← Back to demo</a><span>Recorded study results</span></header><main><p><a href="extraction-failures.html">Explanation of the three extraction failures →</a></p><pre class="results-text">'''+escape(report)+'''</pre></main></body></html>''')

    failures=(ASSETS.parents[1]/'docs/EXTRACTION_FAILURES.md').read_text()
    shell=(out/'results.html').read_text()
    begin=shell.index('<pre class="results-text">')
    end=shell.index('</pre>',begin)
    shell=shell[:begin]+'<pre class="results-text">'+escape(failures)+shell[end:]
    shell=shell.replace('Measured results — muse-guard','Extraction failures — muse-guard').replace('<p><a href="extraction-failures.html">Explanation of the three extraction failures →</a></p>','<p><a href="results.html">← Measured results</a></p>')
    (out/'extraction-failures.html').write_text(shell)
