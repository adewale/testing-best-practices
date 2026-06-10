package suggest

import (
	"sort"
	"testing"
)

var corpus = []string{"hello", "help", "hell", "halo", "world", "word",
	"wired", "spam", "spawn", "span", "spine", "shine"}

func exactTopK(q string, k int) map[string]bool {
	ranked := append([]string(nil), corpus...)
	sort.SliceStable(ranked, func(i, j int) bool {
		return Similarity(q, ranked[i]) > Similarity(q, ranked[j])
	})
	out := map[string]bool{}
	for _, w := range ranked[:k] {
		out[w] = true
	}
	return out
}

func TestSuggestOverlapsExactRanking(t *testing.T) {
	idx := New(corpus)
	k := 5
	for _, q := range []string{"helo", "wrd", "spn"} {
		reference := exactTopK(q, k)
		hits := 0
		for _, w := range idx.Suggest(q, k) {
			if reference[w] {
				hits++
			}
		}
		frac := float64(hits) / float64(k)
		if frac < 0.6 {
			t.Fatalf("overlap %.2f too low for %q", frac, q)
		}
	}
}
