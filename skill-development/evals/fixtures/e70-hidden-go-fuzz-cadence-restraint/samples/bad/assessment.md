# Assessment

This setup is not real fuzzing because each pull request only gives targets 20
seconds. Both targets should run for at least 30 minutes on every PR; increase
the PR `-fuzztime` to `30m` and make the merge gate wait for both campaigns.
Remove the scheduled workflow once the same work runs on pull requests.

`go test ./...` automatically actively fuzzes every `Fuzz...` function anyway,
so the seed corpus and default regression job are redundant and can be dropped.
The matrix is also unnecessary: put both target names in one `-fuzz` expression
so a single invocation runs them together.

Failing artifacts do not need to be committed because future random campaigns
will rediscover them. Longer PR time is the only material improvement.
