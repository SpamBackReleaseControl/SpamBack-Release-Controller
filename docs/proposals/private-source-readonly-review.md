# SpamBack — private-source qualification proposal (INACTIVE)

This is **not an installed GitHub Actions workflow**. It is a draft submitted for independent security review, stored as documentation. **Do not move it into `.github/workflows`, merge as an executable job, provision any keys, or run it without a separate independent authorization.**

This draft has not completed a real private-source fetch, secret containment audit, or failure/revocation exercise. The proposed key must be read-only and restricted to `Spamback/SpamBack-AI`; its public half belongs in the source repo's Deploy keys and its private half must only be entered through a protected, separately owned environment after an approved credential-custody plan. Never paste any key into issues, PR comments, chats, or public repositories.

The dummy controller run #42139085167 remains completed successfully; **do not repeat it**. Apple signing and TestFlight uploading are out of scope.

## Proposed workflow text, for review only

```yaml
# INERT PROPOSAL — intentionally stored outside .github/workflows.
# Requires independent owner code review before installation in controller.
# Source-only private checkout. No signing, build, artifact, release or upload.
name: SpamBack restricted private-source qualification (NO RELEASE)
on:
  issues:
    types: [opened]
permissions: {}
concurrency:
  group: spamback-readonly-source-qualification
  cancel-in-progress: false
jobs:
  inspect_source_only:
    if: >-
      github.repository == 'SpamBackReleaseControl/SpamBack-Release-Controller' &&
      github.ref == 'refs/heads/main' &&
      github.event_name == 'issues' &&
      github.event.action == 'opened' &&
      github.actor == 'Spamback' &&
      github.event.issue.user.login == 'Spamback' &&
      github.event.issue.title == 'SpamBack SOURCE READ-ONLY QUALIFICATION' &&
      github.run_attempt == 1
    environment: TestFlight-Approval
    runs-on: ubuntu-24.04
    timeout-minutes: 6
    permissions: {}
    steps:
      - name: Verify pinned source privately without executing source code
        shell: bash
        env:
          SPAMBACK_SOURCE_READONLY_DEPLOY_KEY: ${{ secrets.SPAMBACK_SOURCE_READONLY_DEPLOY_KEY }}
        run: |
          set -euo pipefail
          umask 077
          test -n "${SPAMBACK_SOURCE_READONLY_DEPLOY_KEY:-}"
          work="$(mktemp -d "$RUNNER_TEMP/spamback-source-XXXXXXXX")"
          trap 'rm -rf -- "$work"' EXIT
          printf '%s\n' "$SPAMBACK_SOURCE_READONLY_DEPLOY_KEY" > "$work/key"
          # GitHub's published, pinned ED25519 host key. Never trust an
          # unverified ssh-keyscan result during a credential-bearing job.
          printf '%s\n' 'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' > "$work/known_hosts"
          test "$(ssh-keygen -lf "$work/known_hosts" -E sha256 | awk '{print $2}')" = 'SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU'
          export GIT_CONFIG_NOSYSTEM=1
          export GIT_CONFIG_GLOBAL=/dev/null
          export XDG_CONFIG_HOME="$work/xdg"
          export GIT_TERMINAL_PROMPT=0
          export GIT_SSH_COMMAND="ssh -i $work/key -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$work/known_hosts -o GlobalKnownHostsFile=/dev/null -o BatchMode=yes -o ForwardAgent=no"
          # Source identity must be reviewed and re-pinned via protected
          # controller PR. Never accept commit/tree from issue body.
          source_commit='13e66d710dc9cda3a76a85c88619336c8ee9f354'
          source_tree='81ec00a5c210890c1e3ecfa6b70cb2f198d8c8f3'
          git clone --quiet --no-checkout -- 'git@github.com:Spamback/SpamBack-AI.git' "$work/source"
          rm -f -- "$work/key"
          unset SPAMBACK_SOURCE_READONLY_DEPLOY_KEY GIT_SSH_COMMAND
          git -C "$work/source" checkout --quiet --detach "$source_commit"
          test "$(git -C "$work/source" rev-parse HEAD)" = "$source_commit"
          test "$(git -C "$work/source" rev-parse 'HEAD^{tree}')" = "$source_tree"
          test "$(git -C "$work/source" rev-parse --is-shallow-repository)" = false
          test -z "$(git -C "$work/source" status --porcelain=v1 --untracked-files=all)"
          test -z "$(git -C "$work/source" ls-files -v | grep -Ev '^H ' || true)"
          test -z "$(git -C "$work/source" ls-files --stage | grep -E '^(120000|160000) ' || true)"
          # Never execute any source scripts; never upload private files.
          echo 'Pinned private-source identity inspected; NO RELEASE.'

```
