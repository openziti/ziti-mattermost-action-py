#!/usr/bin/env bash
# Packages the Wide Attachments plugin into build/com.openziti.wide-attachments-<version>.tar.gz, the bundle a
# Mattermost admin uploads in System Console > Plugins > Plugin Management. Prints the bundle path.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

manifest_field() {
  sed -nE "s/^[[:space:]]*\"$1\"[[:space:]]*:[[:space:]]*\"([^\"]+)\".*/\1/p" "$here/plugin.json" | head -n 1
}
id="$(manifest_field id)"
version="$(manifest_field version)"
[[ -n "$id" && -n "$version" ]] || { echo "plugin.json needs an id and a version" >&2; exit 1; }

build_dir="$here/build"
bundle="$id-$version.tar.gz"

# Mattermost expects one top-level folder in the bundle that holds plugin.json and the webapp files.
rm -rf "${build_dir:?}/$id"
mkdir -p "$build_dir/$id/webapp"
cp "$here/plugin.json" "$build_dir/$id/"
cp "$here/webapp/main.js" "$build_dir/$id/webapp/"

# Relative paths only: GNU tar reads a drive letter such as D: as a remote host name. Numeric root ownership keeps
# the builder's user name out of the committed bundle.
(cd "$build_dir" && tar --owner=0 --group=0 --numeric-owner -czf "$bundle" "$id")
rm -rf "${build_dir:?}/$id"

echo "$build_dir/$bundle"
