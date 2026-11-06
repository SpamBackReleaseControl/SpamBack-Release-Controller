"""Offline tests of fake-key cleanup, no network or real credentials."""
import os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from dummy_credential_lifecycle import rehearse,Refused
def git(*args):return subprocess.check_output(["git",*map(str,args)],text=True).strip()
class LifecycleTests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    self.root=Path(self.tmp.name);src=self.root/"source";src.mkdir()
    git("-C",src,"init","-q")
    git("-C",src,"config","user.name","Test");git("-C",src,"config","user.email","dummy@example.invalid")
    (src/"data.txt").write_text("dummy");git("-C",src,"add",".");git("-C",src,"commit","-qm","dummy")
    self.commit=git("-C",src,"rev-parse","HEAD");self.tree=git("-C",src,"rev-parse","HEAD^{tree}")
    self.bare=self.root/"remote.git";git("clone","--bare","-q",src,self.bare)
    self.work_parent=self.root/"work";self.work_parent.mkdir()
 def call(self,**kw):
    try:return rehearse(self.bare,self.commit,self.tree,self.work_parent,**kw)
    finally:self.assertEqual(list(self.work_parent.iterdir()),[])
 def test_success_still_refuses_release(self):
    r=self.call();self.assertTrue(r["sourcePinMatched"]);self.assertFalse(r["releaseAuthorized"]);self.assertFalse(r["signingEnabled"])
 def test_cleanup_before_clone_failure(self):
    with self.assertRaises(Refused):self.call(fail_at="before_clone")
 def test_cleanup_after_clone_failure(self):
    with self.assertRaises(Refused):self.call(fail_at="after_clone")
 def test_cleanup_after_key_removal_failure(self):
    with self.assertRaises(Refused):self.call(fail_at="after_key_removed")
 def test_cleanup_after_verify_failure(self):
    with self.assertRaises(Refused):self.call(fail_at="after_verify")
 def test_wrong_commit_cleans(self):
    self.commit="f"*40
    with self.assertRaises(Refused):self.call()
 def test_wrong_tree_cleans(self):
    self.tree="f"*40
    with self.assertRaises(Refused):self.call()
 def test_hostile_git_config_cannot_redirect(self):
    with patch.dict(os.environ,{"GIT_CONFIG_COUNT":"1",
         "GIT_CONFIG_KEY_0":"url.file:///does-not-exist/.insteadOf",
         "GIT_CONFIG_VALUE_0":str(self.bare)}):
        self.assertTrue(self.call()["sourcePinMatched"])
 def test_no_network_remote_is_accepted(self):
    with self.assertRaises(Refused):
        rehearse("https://github.com/example/repo",self.commit,self.tree,self.work_parent)
    self.assertEqual(list(self.work_parent.iterdir()),[])
 def test_symlink_remote_refused(self):
    link=self.root/"fake.git";link.symlink_to(self.bare)
    with self.assertRaises(Refused):rehearse(link,self.commit,self.tree,self.work_parent)
 def test_key_not_exposed_in_error(self):
    try:self.call(fail_at="after_clone")
    except Refused as exc:self.assertNotIn("DUMMY_ONLY_NOT_A_CREDENTIAL_9d61fb",str(exc))
    else:self.fail("expected injected failure")
if __name__=="__main__":unittest.main()
