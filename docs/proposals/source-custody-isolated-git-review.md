# Independent review correction — inherited Git settings (NO RELEASE)

**Status: security finding and corrective proposal only.** This file is a
Markdown proposal, not an Actions workflow. It must **not** be copied into
`.github/workflows`, used with a real deploy key, or considered authorization
for Apple signing or TestFlight. The already-approved PR #6 stays unchanged.

## Confirmed issue in PR #6's inert YAML

The original credential-bearing `git clone` line sets
`GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` but leaves
`GIT_CONFIG_COUNT` and `GIT_CONFIG_KEY_*` / `GIT_CONFIG_VALUE_*` inherited.
Git obeys those injected settings even when global and system config are
disabled. A malicious `url.*.insteadOf` mapping can rewrite the apparent
repository destination before an SSH key is used. Therefore **do not activate
the original proposed YAML as written.**

This was reproduced on November 5, 2026 using a disposable local bare
repository, an inherited `GIT_CONFIG_COUNT=1` URL rewrite, and a deliberately
missing substitute remote. The ordinary clone was redirected and refused;
the command below with `env -i` instead cloned the intended local bare
repository and checked out the exact pinned commit. This was **not** a real
private-source fetch or GitHub Actions run.

## Minimal no-secret correction for further review

Invoke every Git command that acts on untrusted source with a fresh
whitelisted environment. Do not pass arbitrary `GIT_*` variables from the
caller, including `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`,
`GIT_SSH`, `GIT_TEMPLATE_DIR`, `GIT_EXEC_PATH`, `GIT_PROXY_COMMAND`
or repository-local config overrides.

Example command structure **for owner review**, NOT a runnable workflow:

```bash
# work and ssh_command must be created by trusted owner-reviewed code.
# Never echo credentials or allow source scripts to run while a key exists.
mkdir -m 700 -- "$work/home"
env -i PATH="$PATH" HOME="$work/home" \
  GIT_TERMINAL_PROMPT=0 GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 \
  GIT_SSH_COMMAND="$ssh_command" \
  git clone --no-checkout -- \
  git@github.com:Spamback/SpamBack-AI.git "$work/source"

# Delete the private key and remove it from the shell environment BEFORE
# checkout/inspection. Subsequent Git calls need the same clean environment.
rm -f -- "$work/key"
unset SPAMBACK_SOURCE_READONLY_DEPLOY_KEY ssh_command
env -i PATH="$PATH" HOME="$work/home" \
  GIT_TERMINAL_PROMPT=0 GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 \
  git -C "$work/source" checkout --detach -- "$owner_reviewed_commit"
```

**Warning:** The code above is only a conceptual hardening example. Before
using any private source key, separately review the complete script for
credential lifetime, remotes, unexpected Git object types, untrusted
attributes/filters, failures and cleanup, and no credential access from
untrusted source. A protected public environment does not automatically
establish source authorization or Apple signing custody.

## Independent prerequisites (NOT DONE)

1. Spouse-controlled protected review of the exact corrected workflow and
   immutable source pins; PR #6 approval does not cover future revisions.
2. A separately approved, **read-only and single-repository** deploy key
   created and entered through account-protected forms only. Do not paste
   either private credentials or recovery data into public files or chat.
3. A dummy-only secret-free failure and cleanup rehearsal before putting
   a real credential in the public controller. No additional Actions run is
   preapproved.
4. Owner-verified revocation, no-public-artifact policy, signer isolation,
   live signed-feed authentication, and a separate explicit TestFlight
   distribution approval. No release authority is granted by this document.

Reference: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
