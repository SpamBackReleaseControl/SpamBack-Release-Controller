"""Offline fake-key lifecycle rehearsal. No SSH/network/signing/release."""
from pathlib import Path
import os,re,shutil,subprocess,tempfile
class Refused(RuntimeError): pass
SHA=re.compile(r"[0-9a-f]{40}\Z")
def _git(env,*cmd):
    r=subprocess.run(["git",*map(str,cmd)],env=env,capture_output=True,text=True,check=False,timeout=20)
    if r.returncode: raise Refused("Dummy source qualification failed")
    return r.stdout.strip()
def rehearse(local_bare,expected_commit,expected_tree,base_dir,*,fail_at=None):
    if fail_at not in (None,"before_clone","after_clone","after_key_removed","after_verify"):
        raise Refused("Unknown dummy failure point")
    if not isinstance(local_bare,Path) or local_bare.is_symlink() or not local_bare.is_dir():
        raise Refused("Only a local bare repository is accepted")
    if not isinstance(base_dir,Path) or base_dir.is_symlink() or not base_dir.is_dir():
        raise Refused("Isolated fixture parent missing")
    if not all(isinstance(v,str) and SHA.fullmatch(v) for v in (expected_commit,expected_tree)):
        raise Refused("Invalid dummy source pins")
    marker="DUMMY_ONLY_NOT_A_CREDENTIAL_9d61fb"
    work=Path(tempfile.mkdtemp(prefix="dummy-custody-",dir=base_dir))
    try:
        os.chmod(work,0o700)
        home=work/"home";home.mkdir(mode=0o700)
        env={"PATH":os.defpath,"HOME":str(home),"GIT_TERMINAL_PROMPT":"0",
             "GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull,"GIT_ATTR_NOSYSTEM":"1"}
        if _git(env,"-C",local_bare,"rev-parse","--is-bare-repository")!="true":
            raise Refused("Local fixture is not bare")
        key=work/"fake-key"
        with key.open("x") as fp:fp.write(marker)
        os.chmod(key,0o600)
        if fail_at=="before_clone":raise Refused("Injected dummy interruption")
        checkout=work/"checkout"
        _git(env,"clone","-q","--no-local","--no-checkout","--",local_bare.resolve(),checkout)
        if fail_at=="after_clone":raise Refused("Injected dummy interruption")
        key.unlink()
        if fail_at=="after_key_removed":raise Refused("Injected dummy interruption")
        _git(env,"-C",checkout,"checkout","-q","--detach",expected_commit)
        if (_git(env,"-C",checkout,"rev-parse","HEAD")!=expected_commit or
              _git(env,"-C",checkout,"rev-parse","HEAD^{tree}")!=expected_tree):
            raise Refused("Dummy Git source pin mismatch")
        if fail_at=="after_verify":raise Refused("Injected dummy interruption")
        return {"dummyOnly":True,"releaseAuthorized":False,"sourcePinMatched":True,"signingEnabled":False}
    finally:shutil.rmtree(work)
