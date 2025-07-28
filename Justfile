build:
  python explode.py

  # for amp
  cp instructions.md AGENT.md
  # for gemini... lol
  cp instructions.md GEMINI.md

clean:
  rm -rf .github .cursor AGENT.md GEMINI.md