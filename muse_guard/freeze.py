"""SHA-256 holdout and study protocol lock. This module never calls a model."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LOCKED_FILES=("study/protocol.json","docs/STUDY.md","muse-guard")+tuple(
    str(path.relative_to(ROOT)) for path in sorted((ROOT/"muse_guard").glob("*.py")))+tuple(
    str(path.relative_to(ROOT)) for path in sorted((ROOT/"datasets/dev").glob("*.json")))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_hashes(root,expected):
    root=Path(root).resolve()
    for name,wanted in expected.items():
        path=root/name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root) or sha(path)!=wanted:
            raise ValueError("Frozen study drift: "+name)


def create_manifest():
    from .rules import PAIRS
    from .quality_gate import validate_pair
    pairs=[pair for pair in PAIRS.values() if pair['split']=='holdout']
    if len(pairs)!=20:raise ValueError('Exactly 20 holdout pairs required')
    accepted=[validate_pair(pair) for pair in pairs]
    files=sorted(path for path in (ROOT/'datasets/holdout').glob('*.json') if path.name!='MANIFEST.json')
    if len(files)!=20:raise ValueError('Exactly 20 holdout data files required')
    return {'schema_version':1,'frozen_on':'2026-10-26','model_calls_on_holdouts_at_freeze':0,
            'holdout_pair_count':20,'holdout_task_count':40,
            'data_files':{str(path.relative_to(ROOT)):sha(path) for path in files},
            'protocol_files':{name:sha(ROOT/name) for name in LOCKED_FILES},
            'quality_gate':accepted}


def verify_freeze():
    path=ROOT/'datasets/holdout/MANIFEST.json'
    if not path.is_file():raise ValueError('Holdouts are not frozen')
    relative="datasets/holdout/MANIFEST.json"
    commits=subprocess.check_output(["git","log","--diff-filter=A","--format=%H","--",relative],cwd=ROOT,text=True).splitlines()
    if len(commits)!=1:raise ValueError("A unique committed freeze anchor is required")
    frozen=subprocess.check_output(["git","show",commits[0]+":"+relative],cwd=ROOT)
    if path.read_bytes()!=frozen:raise ValueError("Frozen manifest changed from its original commit")
    manifest=json.loads(frozen)
    if manifest.get('schema_version')!=1 or manifest.get('holdout_pair_count')!=20 or len(manifest.get('data_files',{}))!=20:
        raise ValueError('Invalid holdout manifest')
    if set(manifest.get('protocol_files',{}))!=set(LOCKED_FILES):raise ValueError('Incomplete protocol lock')
    check_hashes(ROOT,manifest['data_files']);check_hashes(ROOT,manifest['protocol_files'])
    actual={str(path.relative_to(ROOT)) for path in (ROOT/'datasets/holdout').glob('*.json') if path.name!='MANIFEST.json'}
    if actual!=set(manifest['data_files']):raise ValueError('Holdout inventory changed')
    return {'freeze_commit':commits[0],'manifest_sha256':sha(path),'pairs':20,'tasks':40,'protocol':'UNCHANGED'}
