build:
  python explode.py

  # for amp
  cp instructions.md AGENT.md
  # for gemini... lol
  cp instructions.md GEMINI.md
  # for claude
  cp instructions.md CLAUDE.md

clean:
  rm -rf .github .cursor AGENT.md GEMINI.md CLAUDE.md