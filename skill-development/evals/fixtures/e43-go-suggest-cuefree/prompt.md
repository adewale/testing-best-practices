# E40 Go suggestions (cue-free)

A package `suggest` provides `New(words []string) *Index` and `idx.Suggest(q string, k int) []string`, returning the k most similar words — approximately: near-ties may differ between builds. The documented metric is the exported deterministic function `Similarity(a, b string) float64` (higher is more similar). Add Go tests using the standard `testing` package.
