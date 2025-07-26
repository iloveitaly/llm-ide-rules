build:
  python explode.py
  # for amp
  cp instructions.md AGENT.md

clean:
  rm -rf .github .cursor AGENT.md