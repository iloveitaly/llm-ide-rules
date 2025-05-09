copilot2cursor() {
  local input=${1:-.github/copilot-instructions.md}
  mkdir -p .cursor/rules

  # Extract general instructions (before first ##)
  awk '/^## /{exit} {print}' "$input" > /tmp/general_section.md

  cat > .cursor/rules/general.mdc <<EOF
---
description:
alwaysApply: true
---
$(cat /tmp/general_section.md)
EOF

  # Python
  markdown-extract '^## Python' "$input" > /tmp/python_section.md
  cat > .cursor/rules/python.mdc <<EOF
---
description:
globs: "*.py"
alwaysApply: false
---
$(cat /tmp/python_section.md)
EOF

  # React
  markdown-extract '^## React' "$input" > /tmp/react_section.md
  cat > .cursor/rules/react.mdc <<EOF
---
description:
globs: "*.tsx"
alwaysApply: false
---
$(cat /tmp/react_section.md)
EOF

  # Shell Scripts
  markdown-extract '^## Shell Scripts' "$input" > /tmp/shell_section.md
  cat > .cursor/rules/shell.mdc <<EOF
---
description:
globs: "*.sh"
alwaysApply: false
---
$(cat /tmp/shell_section.md)
EOF

  rm /tmp/general_section.md /tmp/python_section.md /tmp/react_section.md /tmp/shell_section.md
  echo "Created Cursor rules in .cursor/rules/"
}