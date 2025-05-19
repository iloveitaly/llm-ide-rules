Coding instructions for all programming languages:

- If no language is specified, assume the latest version of python.
- If tokens or other secrets are needed, pull them from an environment variable
- Prefer early returns over nested if statements.
- Prefer `continue` within a loop vs nested if statements.
- Prefer smaller functions over larger functions. Break up logic into smaller chunks with well-named functions.
- Only add comments if the code is not self-explanatory. Do not add obvious code comments.
- Do not remove existing comments.
- When I ask you to write code, prioritize simplicity and legibility over covering all edge cases, handling all errors, etc.
- When a particular need can be met with a mature, reasonably adopted and maintained package, I would prefer to use that package rather than engineering my own solution.
- Never add error handling to recover gracefully from an error without being asked to do so. Fail hard and early with assertions and allowing exceptions to propagate whenever possible

**DO NOT FORGET**: keep your responses short, dense, and without fluff. I am a senior, well-educated software engineer, and do not need long explanations.

## Fastapi

- When generating a HTTPException, do not add a `detail=` and use a named status code (`status.HTTP_400_BAD_REQUEST`)

## Python

When writing Python:

* Assume the latest python, version 3.13.
* Prefer Pathlib methods (including read and write methods, like `read_text`) over `os.path`, `open`, `write`, etc.
* Prefer modern typing: `list[str]` over `List[str]`, `dict[str, int]` over `Dict[str, int]`, etc.
* Use Pydantic models over dataclass or a typed dict.
* Use SQLAlchemy for generating any SQL queries.
* Use `click` for command line argument parsing.
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

## React Router

- The primary export in a routes file should specify loaderData like `export default function PageName({ loaderData }: Route.ComponentProps)`
- When using an import from `~/configuration/client` (1) use `body:` for request params and (2) always `const { data, error } = await theCall()`

## React

- Do not write any backend code. Just frontend logic.
- For any backend requirements, create mock responses. Use a function to return mock data so I can easily swap it out later.
- When creating mock data, always specify it in a dedicated `mock.ts` file
- Load mock data using a react router `clientLoader`. Use the Skeleton component to present a loading state.
- If a complex skeleton is needed, create a component function `LoadingSkeleton` in the same file.
- Store components for each major page or workflow in `src/components/$WORKFLOW_OR_PAGE_NAME`.
- Use lowercase dash separated words for file names.
- Use React 19, TypeScript, Tailwind CSS, and ShadCN components.
- Prefer function components, hooks over classes.
- Break up large components into smaller components, but keep them in the same file unless they can be generalized.
- Put any "magic" strings like API keys, hosts, etc into a "constants.ts" file.
- Only use a separate interface for component props if there are more than 4 props.
- Internally, store all currency values as integers and convert them to floats when rendering visually
- Never edit the `components/ui/*.tsx` files
- When building forms use React Hook Form.
- Include a two line breaks between any `useHook()` calls and any `useState()` definitions for a component.

### React Hook Form

Follow this structure when generating a form.

```tsx
const formSchema = z.object({
  field_name: z.string(),
  // additional schema definition
})

const form = useForm<z.infer<typeof formSchema>>({
  resolver: zodResolver(formSchema),
})

async function onSubmit(values: z.infer<typeof formSchema>) {
  // ...
}

return (
  <Form {...form}>
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* form fields */}
    </form>
  </Form>
)
```

## Shell

- Assume zsh for any shell scripts. The latest version of modern utilities like ripgrep (rg), fdfind (fd), bat, httpie (http), zq (zed), jq, procs, rsync are installed and you can request I install additional utilities.

## Typescript

- Use `pnpm`, not `npm`
- Node libraries are not available
- Use `lib/` for generic code, `utils/` for project utilities, `hooks/` for React hooks, and `helpers/` for page-specific helpers.
- Prefer `function theName() {` over `const clientLoader = () =>`

