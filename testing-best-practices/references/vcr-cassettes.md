# VCR Cassette Testing

For code that calls external APIs, record real responses once and replay them
in tests. Better than hand-written mocks, cheaper than live API calls in CI.

## How it works

1. First run: real HTTP calls, responses recorded to YAML/JSON files
2. Subsequent runs: responses replayed from cassettes — no network needed
3. Cassettes committed to repo alongside tests
4. To update: delete cassette file and re-run

## Python (pytest-recording / VCR.py)

```python
@pytest.mark.vcr
def test_api_call():
    result = call_external_api("query")
    assert result.status == "ok"

# conftest.py — filter sensitive headers
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["Authorization", "X-API-KEY"]}
```

## TypeScript

Hand-written MSW handlers are deterministic HTTP mocks, not cassettes. They
are useful for controlled errors, auth states, and edge cases, but they do not
prove the shape still matches the real provider. For drift-prone APIs, derive
MSW responses from recorded fixtures or validate them against the provider's
schema/contract.

```typescript
import { readFileSync } from 'node:fs';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const realResponse = JSON.parse(
  readFileSync('tests/fixtures/api/query.ok.json', 'utf8')
);

const server = setupServer(
  http.post('https://api.example.com/v1/query', () => {
    return HttpResponse.json(realResponse);
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

If no recorder exists in the project, treat this as recorded-fixture replay:
refresh the fixture from a real provider response in an explicit, reviewed
workflow, filter secrets, and keep normal CI offline.

## When to use

- Any test calling a third-party API (LLM providers, payment, auth)
- API client libraries
- Integration tests where external service is unreliable or paid

## Gotchas

- Cassettes go stale when APIs change — re-record periodically
- Filter credentials before committing
- Large cassettes bloat the repo — keep them focused
