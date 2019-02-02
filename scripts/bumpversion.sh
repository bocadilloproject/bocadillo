bumpversion "$@"
NEW_VERSION=$(bumpversion --dry-run --list "$@" | grep new_version | sed s,"^.*=",,)
python scripts/changelog_bump.py "$NEW_VERSION" -y
git add -A
git commit -m "bump changelog to $NEW_VERSION"
