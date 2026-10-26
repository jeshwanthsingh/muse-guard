# Study freeze procedure and meaning

Day 3 first settles the gate, CLI, prompts, labels and budgets, then commits the
runtime plus ten dev pairs. It next commits exactly twenty holdout pair files and
their SHA-256 MANIFEST.json, without other code or docs in that commit. Reference
execution is allowed; model execution on holdouts is not authorized today.

The manifest pins every holdout file, all project Python runtime sources, launcher,
operational protocol, original preregistration and ten dev files. Runtime verification
compares the working manifest with its original Git creation commit and inventories
all holdout JSON. Rewriting manifest hashes, adding shadow catalog files or changing
study source cannot be silently accepted. The freeze is an inspectable trusted-repo
protocol lock, not a signature against a compromised host or rewritten Git history.

The study is 10 dev + 20 holdout pairs, 2 twins, 2 repeats and 2 modes: 240 initial
attempts, plus up to 60 guarded conflict recoveries. The original preregistration was
committed before Day 2 results. Day 3 debug runs are exploratory and do not replace
registered repeats. Frozen holdout labels are checker-only; agent-facing IDs do not
name solvability. Guarded study decisions use B; free A/B choice remains for dev.

After freeze, do not modify prompts, labels or budgets. Any necessary future protocol
change must be disclosed as a new study rather than reported under this freeze.
The web view is a later display-only task and must not change the frozen runner.
