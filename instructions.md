Coding instructions for all programming languages:

- If no language is specified, assume the latest version of python.
- If tokens or other secrets are needed, pull them from an environment variable
- Prefer early returns over nested if statements.
- Prefer `continue` within a loop vs nested if statements.
- Prefer smaller functions over larger functions. Break up logic into smaller chunks with well-named functions.
- Only add comments if the code is not self-explanatory. Do not add obvious code comments.
- When I ask you to write code, prioritize simplicity and legibility over covering all edge cases, handling all errors, etc.
- When a particular need can be met with a mature, reasonably adopted and maintained package, I would prefer to use that package rather than engineering my own solution.
- Never add error handling to recover gracefully from an error without being asked to do so. Fail hard and early with assertions and allowing exceptions to propagate whenever possible
- For any complex or critical task, ask any and all clarification questions needed before proceeding.

**DO NOT FORGET**: keep your responses short, dense, and without fluff. I am a senior, well-educated software engineer, and do not need long explanations.

## Python

When writing Python:

* Assume the latest python, version 3.13.
* Prefer Pathlib methods (including read and write methods, like `read_text`) over `os.path`, `open`, `write`, etc.
* Prefer modern typing: `list[str]` over `List[str]`, `dict[str, int]` over `Dict[str, int]`, etc.
* Use Pydantic models over dataclass or a typed dict.
* Use SQLAlchemy for generating any SQL queries.
* Use the `click` package for all command line argument parsing.
* Use `log.info("the message", the_variable=the_variable)` instead of `log.info("the message: %s", the_variable)` or `print` for logging. This object can be found at `from app import log`.
* Log messages should be lowercase with no leading or trailing whitespace.
* No variable interpolation in log messages.
* When a particular need can be met with a mature, reasonably adopted and maintained package, I would prefer to use that package rather than engineering my own solution.

### SQLModel & SQLAlchemy

When writing database models:

* Don't use `Field(...)` unless required. For instance, use `= None` instead of `= Field(default=None)`.
* Add enum classes close to where they are used, unless they are used across multiple classes (then put them at the top of the file)
* Use single double-quote docstrings (a string below the field definition) instead of comments to describe a field's purpose.
* Use `ModelName.foreign_key()` when generating a foreign key field

## Shell Scripts

- Assume zsh for any shell scripts. The latest version of modern utilities like ripgrep (rg), fdfind (fd), bat, httpie (http), zq (zed), jq, procs, rsync are installed and you can request I install additional utilities.

## React

1. Do not write any backend code. Just frontend logic.
2. For any backend requirements, create mock responses. Use a function to return mock data so I can easily swap it out later.
3. When creating mock data, always specify it in a dedicated `mock.ts` file
4. Load mock data using a react router `clientLoader`. Use the Skeleton component to present a loading state.
5. Store components for each major page or workflow in `src/components/$WORKFLOW_OR_PAGE_NAME`.
6. Use lowercase dash separated words for file names.
8. Use React 19, TypeScript, Tailwind CSS, and ShadCN components.
9. Prefer functional components, hooks over classes.
10. Break up large components into smaller components, but keep them in the same file unless they can be generalized.
11. Put any "magic" strings like API keys, hosts, etc into a "constants.ts" file.
12. Only use a separate interface for component props if there are more than 4 props.
13. Internally, store all currency values as integers and convert them to floats when rendering visually
14. use `pnpm` not `npm`
15. Node libraries are not available
16. Never edit the `components/ui/*.tsx` files
