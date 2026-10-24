#!/usr/bin/env bash
# Install the Pages site into a tool repo checkout: writes .github/workflows/pages.yml
# (pinned to the latest gh-pages-site tag by commit SHA) and .github/site/site.toml
# from the example if it does not exist yet. Re-run to bump the pin.
# Usage: install.sh <repo-dir>
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dst="${1:?usage: install.sh <repo-dir>}"
tag="$(git -C "$here" describe --tags --abbrev=0)"
sha="$(git -C "$here" rev-list -n 1 "$tag")"
cd "$dst"
git rev-parse --show-toplevel >/dev/null

slug="$(git remote get-url origin | sed -E 's#(\.git)?$##; s#.*[:/]([^/]+/[^/]+)$#\1#')"
branch="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
[ -n "$branch" ] || branch="$(gh repo view "$slug" --json defaultBranchRef -q .defaultBranchRef.name)"

other="$(grep -lE 'deploy-pages|upload-pages-artifact|gh-pages' .github/workflows/*.y*ml 2>/dev/null \
  | grep -v '/pages.yml$' || true)"
if [ -n "$other" ]; then
  echo "STOP: another Pages workflow already exists: $other" >&2
  exit 2
fi

mkdir -p .github/site .github/workflows
sed -e "s/__BRANCH__/$branch/g" -e "s/__SHA__/$sha/g" -e "s/__TAG__/$tag/g" \
  "$here/templates/pages.yml" > .github/workflows/pages.yml
if [ ! -f .github/site/site.toml ]; then
  install -m 0644 "$here/templates/site.toml" .github/site/site.toml
  echo "created .github/site/site.toml - fill it in from the README"
fi
grep -qxF '_site/' .gitignore 2>/dev/null || echo '_site/' >> .gitignore
echo "installed for $slug (branch $branch, gh-pages-site $tag $sha)"
