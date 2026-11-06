"""Offline test only: verify Git config isolation with disposable bare repositories.

No network, credentials, GitHub Actions, source publishing, or release capability.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


def git(*args, env=None):
    result = subprocess.run(['git', *map(str, args)], env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False, timeout=20)
    if result.returncode:
        raise RuntimeError('dummy Git command failed')
    return result.stdout.strip()


def clean_git_env(home):
    # Equivalent to env -i: never retain arbitrary GIT_*, HOME, or XDG values.
    return {'PATH': os.defpath, 'HOME': str(home), 'GIT_TERMINAL_PROMPT': '0',
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_ATTR_NOSYSTEM': '1'}


class IsolatedSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'isolated_home'
        self.home.mkdir(mode=0o700)
        self.source = self.root / 'source'
        self.source.mkdir()
        git('init', '-q', self.source)
        git('-C', self.source, 'config', 'user.name', 'Dummy')
        git('-C', self.source, 'config', 'user.email', 'test@example.invalid')
        (self.source / 'source.txt').write_text('no-secret dummy\n')
        git('-C', self.source, 'add', 'source.txt')
        git('-C', self.source, 'commit', '-qm', 'fixture')
        self.pin = git('-C', self.source, 'rev-parse', 'HEAD')
        self.tree = git('-C', self.source, 'rev-parse', 'HEAD^{tree}')
        self.remote = self.root / 'bare.git'
        git('clone', '--bare', '-q', self.source, self.remote)

    def clone(self):
        dest = self.root / 'checkout'
        git('clone', '-q', '--no-local', '--no-checkout', '--', self.remote,
            dest, env=clean_git_env(self.home))
        git('-C', dest, 'checkout', '-q', '--detach', self.pin,
            env=clean_git_env(self.home))
        self.assertEqual(git('-C', dest, 'rev-parse', 'HEAD',
                             env=clean_git_env(self.home)), self.pin)
        self.assertEqual(git('-C', dest, 'rev-parse', 'HEAD^{tree}',
                             env=clean_git_env(self.home)), self.tree)

    def test_exact_local_clone_non_authorizing(self):
        self.clone()

    def test_inherited_git_config_count_does_not_rewrite(self):
        with patch.dict(os.environ, {'GIT_CONFIG_COUNT': '1',
              'GIT_CONFIG_KEY_0': 'url.file:///missing-fixture/.insteadOf',
              'GIT_CONFIG_VALUE_0': str(self.remote)}):
            self.clone()

    def test_inherited_git_config_global_does_not_rewrite(self):
        cfg = self.root / 'evil.gitconfig'
        cfg.write_text('[url "file:///missing-fixture/"]\n    insteadOf = '
                       + str(self.remote) + '\n')
        with patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': str(cfg)}):
            self.clone()

    def test_inherited_git_config_parameters_does_not_rewrite(self):
        with patch.dict(os.environ, {'GIT_CONFIG_PARAMETERS':
                        "'url.file:///missing-fixture/.insteadOf="+str(self.remote)+"'"}):
            self.clone()

    def test_inherited_git_template_dir_does_not_apply(self):
        template = self.root / 'template'
        (template / 'hooks').mkdir(parents=True)
        (template / 'hooks' / 'post-checkout').write_text('#!/bin/sh\nexit 66\n')
        (template / 'hooks' / 'post-checkout').chmod(0o755)
        with patch.dict(os.environ, {'GIT_TEMPLATE_DIR': str(template)}):
            self.clone()

    def test_inherited_git_exec_path_is_ignored(self):
        with patch.dict(os.environ, {'GIT_EXEC_PATH': '/missing-git-executables'}):
            self.clone()

    def test_inherited_home_global_config_is_ignored(self):
        hostile_home = self.root / 'evil-home'
        hostile_home.mkdir()
        (hostile_home / '.gitconfig').write_text('[url "file:///missing-fixture/"]\n'
                      '    insteadOf = '+str(self.remote)+'\n')
        with patch.dict(os.environ, {'HOME': str(hostile_home)}):
            self.clone()


if __name__ == '__main__':
    unittest.main()
