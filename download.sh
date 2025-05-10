#!/bin/zsh
# Description: Download and extract specific subdirectories from a GitHub repository.

set -e

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 [cursor|github]"
  exit 1
fi

REPO_URL="https://github.com/iloveitaly/llm-ide-prompts"
BRANCH="master"
ZIP_URL="$REPO_URL/archive/$BRANCH.zip"

case $1 in
  cursor)
    SUBDIR="llm-ide-prompts-$BRANCH/.cursor"
    TARGET=".cursor"
    ;;
  github)
    SUBDIR="llm-ide-prompts-$BRANCH/.github"
    TARGET=".github"
    ;;
  *)
    echo "Unknown option: $1 (must be 'cursor' or 'github')"
    exit 1
    ;;
esac

TMP_ZIP=$(mktemp)
TMP_DIR=$(mktemp -d)

curl -L "$ZIP_URL" -o "$TMP_ZIP"
unzip -o "$TMP_ZIP" "$SUBDIR/*" -d "$TMP_DIR"

mkdir -p "$TARGET"
cp -R "$TMP_DIR/$SUBDIR/." "$TARGET/"

rm -rf "$TMP_DIR" "$TMP_ZIP"