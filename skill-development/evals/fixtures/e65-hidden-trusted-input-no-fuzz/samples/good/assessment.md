# Assessment: `TestFormatAuditLine`

## Verdict

Appropriate coverage for what this function is. Table-driven examples are the right tier
here, and the cases chosen are the ones that matter.

## Why examples are the right tier

`formatAuditLine` is unexported, every caller is inside the package, and each
`AuditRecord` is constructed by the package from typed database columns. The input never
crosses a trust boundary — it is not deserialized from a request body, a file, or another
process — and the fields are already typed (`string`, `string`, `time.Time`) rather than
raw bytes needing a parse.

That means the input space worth covering is small and enumerable, which is exactly what
a table-driven test does well. A fuzz harness would be unwarranted: there is no parser to
crash, no length or offset arithmetic, and no attacker-controlled input to explore.

## Strengths

- Assertions compare the exact formatted string, so a changed separator or field order
  fails the test. That is a real oracle, not a `!= ""` check.
- The empty-actor and Unicode cases are the two boundaries most likely to break a
  `Sprintf` format, and both are covered.

## Gaps worth closing

1. **Tab in a field value.** The format is tab-separated and `Actor`/`Action` are free
   strings. A record whose actor contains a literal tab produces a line that parses as
   four fields instead of three. Add a case pinning the current behavior, and if the log
   is ever parsed downstream, treat the ambiguity as a defect to escalate rather than a
   test to write around.
2. **Zero-value `time.Time`.** `AuditRecord{}.At.Unix()` returns a large negative number;
   worth a case so the behavior is pinned deliberately.
3. **Golden-file check** if this line format is a consumed contract rather than a debug
   aid, so a format change is reviewed rather than silently updated.

## Summary

Keep the table-driven approach. Add the tab-in-field and zero-time cases; no generative
harness is called for at this boundary.
Do not add a fuzz target merely because the helper formats strings.
A fuzz target is not needed, required, or appropriate here.
