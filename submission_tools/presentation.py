"""Opt-in display hooks for the submission CLI; original study modules stay intact."""
from contextlib import contextmanager
from muse_guard import view,recovery
from muse_guard.rules import TASKS
from submission_tools.decision_preview import html_preview,cli_preview

_original_render=view.render
_original_choose=recovery.choose_decision


def render(row,**kwargs):
    page=_original_render(row,**kwargs)
    req=view.display_requirements(row)
    if req.get('input_space'):
        extra=html_preview(req)
        # Immediately before the choice, not among code-check results.
        marker='<section aria-labelledby="decision-title">'
        if marker in page:page=page.replace(marker,extra+marker,1)
        else:page=page.replace('<main>','<main>'+extra,1)
    return page


@contextmanager
def display_hooks(task_name=None):
    """One CLI process; no hook is imported by the frozen study executor."""
    previous_render=view.render;previous_choose=recovery.choose_decision
    def choose(rule_ids,decide=None,input_fn=None):
        if task_name in TASKS:print(cli_preview(TASKS[task_name]['requirements']),flush=True)
        return _original_choose(rule_ids,decide,input_fn)
    view.render=render;recovery.choose_decision=choose
    try:yield
    finally:view.render=previous_render;recovery.choose_decision=previous_choose


def main():
    import sys
    from muse_guard.cli import main as original_main
    args=sys.argv[1:]
    with display_hooks(args[1] if args and args[0]=='run' and len(args)>1 else None):original_main()
