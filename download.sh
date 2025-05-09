#!/bin/zsh
# https://github.com/iloveitaly/llm-ide-prompts

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

curl -L "$ZIP_URL" -o repo.zip
unzip -o repo.zip "$SUBDIR/*" -d tmp_extract
rm -rf "$TARGET"
mv "tmp_extract/$SUBDIR" "$TARGET"
rm -rf tmp_extract repo.zip