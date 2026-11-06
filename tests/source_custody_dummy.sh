#!/usr/bin/env bash
# DUMMY LOCAL-ONLY; no real credentials, signing, source code or networking.
set -euo pipefail
umask 077
[[ $# == 4 ]] || { echo 'local dummy arguments required' >&2; exit 2; }
remote="$1"; expected_commit="$2"; expected_tree="$3"; scratch="$4"
[[ "$remote" = /* && -d "$remote" && ! -L "$remote" ]] || exit 3
[[ "$expected_commit" =~ ^[0-9a-f]{40}$ && "$expected_tree" =~ ^[0-9a-f]{40}$ ]] || exit 4
[[ -d "$scratch" && ! -L "$scratch" ]] || exit 5
work="$(mktemp -d "$scratch/dummy-custody-XXXXXXXX")"
cleanup() { rm -rf -- "$work"; }
trap cleanup EXIT
mkdir -m 700 "$work/home"
printf 'DUMMY-NOT-A-PRIVATE-KEY\n' > "$work/dummy-key"
if [[ "${INJECT_FAILURE:-}" == before_clone ]]; then exit 6; fi
# A local path plus isolated Git environment; no network protocol accepted.
env -i PATH="$PATH" HOME="$work/home" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 git clone -q --no-local --no-checkout -- "$remote" "$work/source" 2>/dev/null || exit 7
if [[ "${INJECT_FAILURE:-}" == after_clone ]]; then exit 8; fi
rm -f -- "$work/dummy-key"
if [[ "${INJECT_FAILURE:-}" == after_key_removed ]]; then exit 9; fi
env -i PATH="$PATH" HOME="$work/home" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 git -C "$work/source" checkout -q --detach "$expected_commit" 2>/dev/null || exit 10
[[ "$(env -i PATH="$PATH" HOME="$work/home" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null git -C "$work/source" rev-parse HEAD)" == "$expected_commit" ]] || exit 11
[[ "$(env -i PATH="$PATH" HOME="$work/home" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null git -C "$work/source" rev-parse 'HEAD^{tree}')" == "$expected_tree" ]] || exit 12
if [[ "${INJECT_FAILURE:-}" == after_verify ]]; then exit 13; fi
printf 'LOCAL_DUMMY_MATCHED_NO_RELEASE\n'
