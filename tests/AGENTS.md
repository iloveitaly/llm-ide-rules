## Pytest Integration Tests


- Look to `app/factories/` to generate any required database state
  - Here's an example of how to create + persist a factory `DistributionFactory.save(domain=PYTHON_TEST_SERVER_HOST)`
- Add the `server` factory to each test
- Use the `faker` factory to generate emails, etc.
- Don't add obvious `assert` descriptions
- Do not use the `db_session` fixture here. Instead, use `with test_session():` if you need to setup complex database state
- if a UI timeout is occuring, it could be because it cannot find a element because the rendering has changed. Check the failure screenshot and see if you can correct the test assertion.
- The integration tests can take a very long time to run. Do not abort them if they are taking a long time.
- Use `expect(page.get_by_text("Screening is fully booked")).to_be_visible()` instead of `expect(page.get_by_role("heading")).to_contain_text("Screening is fully booked")`. It's less brittle.
- Do not use `client` fixtures in an integration test. Integration tests should only use the frontend of the website to interact with the application, not the API.
- Use `with page.expect_response("https://example.com/resource") as response_info:` to assert against network activity.
- Do not `next_button.evaluate("el => el.click()")` instead, just `locator.click()`. If this doesn't work, stop your work and let me know.
- Only use `wait_for_loading(page)` if a `LONG_INTEGRATION_TEST_TIMEOUT` on an expectation does not work: `expect(page.get_by_text("Your Matched Doctors")).to_be_visible(timeout=LONG_INTEGRATION_TEST_TIMEOUT)`
  - `LONG_INTEGRATION_TEST_TIMEOUT` should only be used as a last resort. If you have many of these in a test, let me know and I will debug it.
- Prefer fewer integration tests that cover more functionality. Unlike unit tests, where each test is designed to test a very particular piece of functionality, I want integration tests to cover entire workflows. It's preferred to add more steps to an integration test to test an entire workflow.
- Prefer simple locators. If a `filter`, `or_`, etc is required to capture a button in multiple states it indicates something is wrong in the code.
- Use `react_router_url` to generate the frontend url path and do not set `base_url`.
- End all Playwright tests with `from pytest_playwright_artifacts import assert_no_console_errors` and `assert_no_console_errors(request)` (capture is the plugin's `playwright_console_logging` fixture).
  - Test-Specific Ignores: Pass `ignore=[...]` to `assert_no_console_errors` per `pytest-playwright-artifacts` (regex strings, compiled patterns, or `{"file": "...", "message": "..."}` dicts); add a comment explaining why.
  - Global Ignores: Use `playwright_console_ignore` under `[tool.pytest.ini_options]` in `pyproject.toml` (see `pytest-playwright-artifacts` README).

### Example Integration Test

Below is an example test. Notice the following:

- Code comments are used to describe the key user steps that are being tested
- We avoid long timeouts or wait commands
- Fixtures and factories are generated at the beginning of the test
- We assert against database state after each major user action
- Some of the comments (i.e. comments on included fixtures) are included for instructional purposes only and should not be included in the tests you write

```python
from pytest_playwright_artifacts import assert_no_console_errors


def test_streaming_checkout_creates_user_and_links_order(
    # this fixture ensures that the underlying python server is started
    server,
    faker,
    page: Page,
    # if you need to create objects (like factories) tied to a common session, include this fixture
    db_truncate_session,
    # for asserting against the console logs
    request: FixtureRequest,
) -> None:
    distribution = DistributionWithWebhooksFactory.save()
    test_email = clerk_test_email()

    # 1) Run through streaming checkout
    page.goto(react_router_url("/streaming"))

    page.get_by_placeholder("your@email.com").first.fill(test_email)
    page.get_by_placeholder("your@email.com").last.fill(test_email)

    # Check TOS
    page.get_by_role("checkbox").last.check()

    fill_stripe_checkout(page)

    # 2) Complete checkout
    # the stripe checkout form will expand and cause the purchase button to move below the screen
    safely_scroll_then_click(page.get_by_role("button", name="Complete Purchase"))

    expect(page.get_by_role("heading", name="You're ready to watch!")).to_be_visible()
    page.get_by_role("link", name="Login & Start Watching").click()

    # 3) Assert against database and Clerk state

    # One StreamingOrder should be created for this distribution and email
    assert StreamingOrder.count() == 1
    streaming_order = StreamingOrder.get(email=test_email)
    assert streaming_order

    assert streaming_order.status.value == "completed"
    assert streaming_order.user_id is not None

    # 4) Login to the app via the Clerk login page
    clerk_login_and_verify(page, test_email)

    expect(page.get_by_text("Triumph of the Heart").first).to_be_visible()

    # 5) Play the video
    page.get_by_role("button").filter(has_text="Play").click()

    # wait for the page to completely load
    wait_for_loading(page)

    expect(page.get_by_text("Triumph of the Heart").first).to_be_visible()
    expect(page.get_by_text("Play")).not_to_be_visible()

    assert_no_console_errors(
        request,
        ignore=[
            {
              # if there are console errors specific to the project, exclude them here. Match to the specific URL if you can.
              "file": r"https://iframe.cloudflarestream.com/.*",
              "message": "the server responded with a status of 403",
            }
        ],
    )
```


## Pytest Tests


- Look first to `app.factories.*` instead of `app.models.*` to generate any required database state
  - For example, to create and persist a `Distribution` record `DistributionFactory.save()`
  - If a factory doesn't exist for the model you are working with, create one.
  - You can customize one or more params in a factory using `DistributionFactory.save(host="custom_host.com)`
- Use `faker` factory to generate emails, etc.
- Do not mock or patch unless I instruct you to. Test as much of the application stack as possible in each test.
- If you get lazy attribute errors, or need a database session to share across logic, use the `db_session` fixture to fix the issue.
  - Note that when writing route tests a `db_session` is not needed for the logic inside of the route.
- When testing Stripe, use the sandbox API. Never mock out Stripe interactions unless explicitly told to.
- Omit obvious docstrs and comments. Add comments for non-obvious but easy-to-miss lines that are key to what the test is checking.
- If a docstring needs formatting, use markdown.

### Example Test

Below is an example test, you'll notice the following:

- Docstr is omitted since the purpose of the test is obvious
- Comment about the `county` is added since it's the main point of the test
- Newline between test setup, functionality under test, and assertions against result
- `api_app_url_path_for` helper is used instead of hardcoded routes

```python
from app.generated.fastapi_typed_routes import api_app_url_path_for
import json

def test_calculate_quote_unknown_county(client):
    payload = {
        "subscriber": {"age": 35, "gender": "M"},
        # fake county to ensure error is thrown
        "county": "NotACounty",
    }

    response = client.post(
        api_app_url_path_for("composite_quote"),
        json=payload,
    )

    assert_status(response, status.HTTP_422_UNPROCESSABLE_ENTITY)
```

### File Structure

* If there's more than a handful of tests in a folder, you should probably create subfolders.
* File name should be related to the file or primary class / functionality the test is covering. Do not add a component to the test name that exists in the test file path.
  * Example: `app/routes/unauthenticated/quote.py` should be `tests/routes/unauthenticated/quote_test.py`
* `tests/routes/{unauthenticated,authenticated}` and a handful of top-level test files for fastapi API route testing.
* `tests/integration/` for browser tests


## Python Route Tests


- Polyfactory is the [factory](app/factories/) library in use. `ModelNameFactory.build()` is how you generate factories.
- Use `assert_status(response)` instead of `assert response.status_code == status.HTTP_200_OK`
- Do not reference routes by raw strings. Instead, use the typed route helpers defined in `app/generated/fastapi_typed_routes.py`.
