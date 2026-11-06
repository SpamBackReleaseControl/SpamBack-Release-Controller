# SpamBack — corrected private-source custody review request (NO RELEASE)

**Requested decision:** Review this updated, documentation-and-dummy-test-only
design. **No approval here authorizes a credential, GitHub Actions run, merge
of executable workflows, Apple signing or TestFlight distribution.**

## What was wrong with the earlier PR #6 proposal

The original *inert Markdown* in public-controller PR #6 contained an
example `git clone` that did not discard inherited `GIT_CONFIG_COUNT`,
`GIT_CONFIG_PARAMETERS` and related configuration overrides. A clone
destination could be rewritten despite setting `GIT_CONFIG_GLOBAL=/dev/null`.
**Do not activate the example from PR #6.** PR #6 is still open and unchanged;
its approval belongs to that exact older document only.

## Corrected approach and exact scope

1. Keep the real controller's already-approved `TestFlight-Approval`
   environment and its protected `main`. Request a **new independent
   review** for the eventual exact workflow; do not reuse approval of PR #6
   to authorize credential use.
2. A future source-only controller job must be pinned to immutable Git
   commit and tree IDs independently checked against the private repository
   through authenticated owner-controlled access. GitHub branch protection
   for the private `main` remains absent, so matching a draft SHA alone
   is not signing authorization.
3. After a *separate owner approval*, provision a private-source-only
   **read-only** deploy key through GitHub's protected account settings.
   Enter the private key only into an independently controlled, protected
   environment; do not print it or store it in repository files, PR comments,
   chats, or artifacts. No key exists for this proposal.
4. Use `env -i` and allowlist only essential environment variables on
   **every** Git operation. Establish a private temporary `HOME`, fixed
   GitHub SSH host key and fingerprint, private SSH key-file permissions,
   strict host checking, no agent forwarding, and no untrusted Git hooks.
   Remove the key before checking out or running any untrusted source.
5. Reject unexpected source identity, tree identity, submodules, symlinks,
   altered working tree, unverified runner settings, ambiguous review/rerun
   evidence, and interrupted credential cleanup. Never execute source
   scripts with credentials accessible.
6. Ensure private source and signing assets remain absent from public
   artifacts/logs. **Do not install Apple signing secrets in the public
   controller** until a separately reviewed build-and-signer isolation
   design exists.
7. Require a separately approved revocation test: remove the deploy key
   from the source repository, verify access is denied, and revoke the
   associated protected secret after the controlled qualification. Do
   not assume that deleting a local file revokes an SSH deploy key.

## What has actually been checked

- Independently spouse-approved dummy controller run `42139085167`
  completed successfully on its first attempt. It did **not** fetch
  private source, sign anything, or upload an artifact.
- Exact committed private-app source verifier: 12/12 local tests passed.
- Local-only source-handoff rehearsal: 13/13 local tests passed.
- Developer-fork Git environment-isolation fixture: 7/7 local tests
  passed, with exact committed file hash matched.
- Developer-fork dummy credential-cleanup fixture: 11/11 local tests
  passed, with exact committed file hashes matched.
- The dummy cleanup fixture uses a harmless marker, not SSH credentials.
  These results do **not** validate real private-source access, production
  secret containment, revocation, Apple signing, or TestFlight.

## Hard gates before any activation

- [ ] Spouse independently reviews and approves the corrected **exact**
      source-only workflow code and immutable source pins.
- [ ] Source administrator approves one-repository read-only credential
      creation after a written authorization/revocation plan.
- [ ] Explicit separate approval for any new GitHub Actions execution.
- [ ] Real private-source fetch and credential revocation independently
      qualified without exposure in logs/artifacts.
- [ ] Source build scripts and signing boundary independently audited.
- [ ] Live protected signed feed authenticated, then Apple distribution
      approved explicitly.

**Current decision: NO-GO.** No production source/secret/signing workflow
can be enabled from these documents or dummy tests alone.
