---
applyTo: "app/routes/**/*.py"
---
- When generating a HTTPException, do not add a `detail=` and use a named status code (`status.HTTP_400_BAD_REQUEST`)
