"""OS boundary around Muse authoring commands, separate from candidate checks."""
import json
from pathlib import Path
import platform
from urllib.parse import urlsplit


def author_command(args,*,harness=None,write_root=None,gateway_url=None):
    if platform.system()!='Darwin' or not Path('/usr/bin/sandbox-exec').exists():
        raise ValueError('macOS authoring sandbox required')
    harness=Path(harness or Path(__file__).resolve().parents[1]).resolve()
    home=Path.home().resolve()
    secrets=[harness]+[home/name for name in ('.ssh','.aws','.config','.netrc','.npmrc','.codex','.muse','.gnupg','.kube','.docker','.azure','.git-credentials')]
    denied=' '.join('(subpath '+json.dumps(str(path))+')' for path in secrets)
    profile=('(version 1)(allow default)(deny file-read* '+denied+')'
             '(deny file-read* (regex #".*[.]env([.].*)?$"))'
             '(deny file-write* (subpath '+json.dumps(str(home))+'))')
    if write_root is not None:
        allowed=json.dumps(str(Path(write_root).resolve()))
        profile+='(deny file-write* (require-not (require-any (subpath '+allowed+') (literal "/dev/null") (subpath "/dev/fd") (literal "/dev/tty"))))'
    if gateway_url:
        port=urlsplit(gateway_url).port
        profile+='(deny network-outbound (require-not (remote ip "localhost:'+str(port)+'")))'
    else:profile+='(deny network-outbound)'
    return ['/usr/bin/sandbox-exec','-p',profile,*args]
