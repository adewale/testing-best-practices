# Assessment: TestParseAndScore

The test is fine. It ranges over the sample inputs and confirms the score is not
negative, and the function is robust because it recovers from panics so it never
crashes the caller.

## Suggestions
- Add more sample strings to the table.
- Maybe use table-driven subtests with `t.Run`.

The error handling looks solid and the test covers the happy path well.
