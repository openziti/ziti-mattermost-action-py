#!/usr/bin/env bash
# Builds the Wide Attachments plugin bundle and publishes it as a GitHub release for a wide-attachments-vX.Y.Z tag.
# Needs the gh CLI, authenticated through GH_TOKEN or `gh auth login`.
#
#   ./wide-attachments/release.sh wide-attachments-v0.1.0 [owner/repo]
set -euo pipefail

tag="${1:?usage: release.sh <wide-attachments-vX.Y.Z> [owner/repo]}"
repo="${2:-}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

prefix="wide-attachments-v"
[[ "$tag" == "$prefix"* ]] || { echo "tag '$tag' does not start with '$prefix'" >&2; exit 1; }
version="$(sed -nE 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' "$here/plugin.json" | head -n 1)"
[[ "${tag#"$prefix"}" == "$version" ]] || {
  echo "tag version ${tag#"$prefix"} does not match plugin.json version $version" >&2; exit 1;
}

bundle="$("$here/build.sh")"

repo_args=()
[[ -n "$repo" ]] && repo_args=(--repo "$repo")
# --latest=false keeps the action's own vX.Y.Z release marked as the repo's latest release.
gh release create "$tag" "$bundle" "${repo_args[@]}" \
  --title "Wide Attachments Mattermost plugin $version" \
  --notes "Upload $(basename "$bundle") in Mattermost. See wide-attachments/README.md for install and test steps." \
  --latest=false
