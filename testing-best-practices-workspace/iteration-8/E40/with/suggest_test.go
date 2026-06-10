package suggest

import (
	"fmt"
	"math/rand"
	"sort"
	"strings"
	"testing"
)

// bruteForceTopK is the brute-force oracle: scan every word, rank by
// Similarity, and return the k highest-scoring words. It is deliberately
// simple so it can carry no subtle bugs.
func bruteForceTopK(words []string, q string, k int) []string {
	type scored struct {
		word  string
		score float64
	}
	scores := make([]scored, len(words))
	for i, w := range words {
		scores[i] = scored{w, Similarity(q, w)}
	}
	sort.SliceStable(scores, func(i, j int) bool {
		return scores[i].score > scores[j].score
	})
	out := make([]string, 0, k)
	for i := 0; i < k && i < len(scores); i++ {
		out = append(out, scores[i].word)
	}
	return out
}

// TestSuggestRecallAgainstBruteForce tests that Suggest returns results that
// overlap well with the brute-force oracle — the core statistical test for an
// approximate matcher. The threshold of >= 0.80 recall is generous enough to
// survive near-tie ties across builds but tight enough to catch real
// regressions (a naive random-pick implementation would score ~0.05).
func TestSuggestRecallAgainstBruteForce(t *testing.T) {
	// Seed pinned so "approximate" never means "flaky".
	rng := rand.New(rand.NewSource(42))

	// Build a vocabulary of random-ish words to simulate realistic input.
	vocab := makeVocab(rng, 500)
	idx := New(vocab)

	const k = 10
	const queries = 50
	const recallThreshold = 0.80

	totalRecall := 0.0
	for i := 0; i < queries; i++ {
		// Pick a query word from the vocab (so we know there is at least one
		// exact match), occasionally mutate it to exercise fuzzy paths.
		base := vocab[rng.Intn(len(vocab))]
		q := mutate(rng, base)

		approx := idx.Suggest(q, k)
		exact := bruteForceTopK(vocab, q, k)

		approxSet := toSet(approx)
		exactSet := toSet(exact)

		overlap := 0
		for w := range approxSet {
			if exactSet[w] {
				overlap++
			}
		}
		denom := len(exactSet)
		if denom == 0 {
			denom = 1
		}
		totalRecall += float64(overlap) / float64(denom)
	}

	meanRecall := totalRecall / float64(queries)
	if meanRecall < recallThreshold {
		t.Errorf("mean recall %.3f is below threshold %.2f over %d queries (seed=42)",
			meanRecall, recallThreshold, queries)
	}
}

// TestSuggestResultsAreValidWords checks that every string returned by Suggest
// is a word that was actually in the original word list. An approximate index
// must never fabricate words.
func TestSuggestResultsAreValidWords(t *testing.T) {
	rng := rand.New(rand.NewSource(7))
	vocab := makeVocab(rng, 200)
	vocabSet := toSet(vocab)
	idx := New(vocab)

	queries := []string{"hello", "world", "test", "golang", "foo"}
	for _, q := range queries {
		results := idx.Suggest(q, 5)
		for _, r := range results {
			if !vocabSet[r] {
				t.Errorf("Suggest(%q, 5) returned %q which is not in the vocabulary", q, r)
			}
		}
	}
}

// TestSuggestReturnsAtMostK verifies the length contract: Suggest(q, k) must
// return at most k results. It may return fewer when the vocabulary is small.
func TestSuggestReturnsAtMostK(t *testing.T) {
	words := []string{"apple", "application", "apply", "apt", "banana", "band"}
	idx := New(words)

	cases := []struct {
		q string
		k int
	}{
		{"app", 3},
		{"app", 10}, // k > len(words) — must not panic, return <= len(words)
		{"xyz", 2},
		{"apple", 1},
	}
	for _, tc := range cases {
		results := idx.Suggest(tc.q, tc.k)
		if len(results) > tc.k {
			t.Errorf("Suggest(%q, %d) returned %d results, want at most %d",
				tc.q, tc.k, len(results), tc.k)
		}
	}
}

// TestSuggestNoDuplicates verifies that no word appears twice in the result
// list, regardless of how the index breaks ties.
func TestSuggestNoDuplicates(t *testing.T) {
	words := []string{"cat", "bat", "hat", "rat", "sat", "fat", "mat", "pat"}
	idx := New(words)

	results := idx.Suggest("cat", len(words))
	seen := make(map[string]bool)
	for _, r := range results {
		if seen[r] {
			t.Errorf("Suggest returned duplicate word %q", r)
		}
		seen[r] = true
	}
}

// TestSuggestResultsOrderedBySimilarity checks the invariant that the returned
// slice is non-increasing in Similarity score. The problem statement says
// near-ties may differ, but the ordering of clearly separated scores must be
// respected.
func TestSuggestResultsOrderedBySimilarity(t *testing.T) {
	words := []string{"apple", "application", "apply", "banana", "carrot", "date"}
	idx := New(words)

	results := idx.Suggest("appl", 4)
	for i := 1; i < len(results); i++ {
		prev := Similarity("appl", results[i-1])
		curr := Similarity("appl", results[i])
		if curr > prev+1e-9 {
			t.Errorf("results not sorted: Similarity(%q, %q)=%.6f > Similarity(%q, %q)=%.6f",
				"appl", results[i], curr, "appl", results[i-1], prev)
		}
	}
}

// TestSuggestExactMatchRanksFirst verifies that when the query is exactly one
// of the vocabulary words, that word appears in the top result (Similarity of
// a word with itself should be maximal among vocabulary members).
func TestSuggestExactMatchRanksFirst(t *testing.T) {
	words := []string{"golang", "goland", "golangci", "gopher", "python", "ruby"}
	idx := New(words)

	result := idx.Suggest("golang", 1)
	if len(result) == 0 {
		t.Fatal("Suggest returned empty slice for exact vocabulary query")
	}
	if result[0] != "golang" {
		t.Errorf("Suggest(%q, 1) = [%q], want [\"golang\"]", "golang", result[0])
	}
}

// TestSuggestEmptyQuery checks that an empty query does not panic and returns
// at most k results.
func TestSuggestEmptyQuery(t *testing.T) {
	words := []string{"foo", "bar", "baz"}
	idx := New(words)

	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Suggest panicked on empty query: %v", r)
		}
	}()
	results := idx.Suggest("", 2)
	if len(results) > 2 {
		t.Errorf("Suggest(\"\", 2) returned %d results, want at most 2", len(results))
	}
}

// TestSuggestEmptyVocabulary checks that building an index on an empty word
// list and querying it does not panic and returns an empty slice.
func TestSuggestEmptyVocabulary(t *testing.T) {
	idx := New([]string{})

	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Suggest on empty vocab panicked: %v", r)
		}
	}()
	results := idx.Suggest("anything", 5)
	if len(results) != 0 {
		t.Errorf("Suggest on empty vocab returned %v, want []", results)
	}
}

// TestSuggestKZero checks that requesting k=0 results returns an empty slice
// without panicking.
func TestSuggestKZero(t *testing.T) {
	idx := New([]string{"alpha", "beta", "gamma"})

	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Suggest(q, 0) panicked: %v", r)
		}
	}()
	results := idx.Suggest("alpha", 0)
	if len(results) != 0 {
		t.Errorf("Suggest(%q, 0) = %v, want []", "alpha", results)
	}
}

// TestSuggestTopKBetterThanRandom validates the statistical oracle more
// strictly: the average Similarity of results returned by Suggest must be
// higher than the average Similarity of a random sample of the same size.
// A real approximate matcher must do better than random selection.
func TestSuggestTopKBetterThanRandom(t *testing.T) {
	rng := rand.New(rand.NewSource(99))
	vocab := makeVocab(rng, 300)
	idx := New(vocab)

	const k = 5
	const trials = 40
	const marginFactor = 1.5 // suggested results must be at least 1.5x better

	for i := 0; i < trials; i++ {
		q := vocab[rng.Intn(len(vocab))]
		results := idx.Suggest(q, k)

		if len(results) == 0 {
			continue
		}

		suggestedAvg := averageSimilarity(q, results)

		// Sample k random words (not necessarily distinct, intentional simplicity).
		randomSample := make([]string, k)
		for j := range randomSample {
			randomSample[j] = vocab[rng.Intn(len(vocab))]
		}
		randomAvg := averageSimilarity(q, randomSample)

		// Only assert when random avg is non-trivial to avoid division-by-zero
		// noise on degenerate inputs.
		if randomAvg > 0 && suggestedAvg < marginFactor*randomAvg {
			t.Errorf("trial %d: Suggest avg similarity %.4f not %gx better than random avg %.4f for query %q",
				i, suggestedAvg, marginFactor, randomAvg, q)
		}
	}
}

// TestSimilaritySymmetry checks that Similarity(a,b) == Similarity(b,a).
func TestSimilaritySymmetry(t *testing.T) {
	pairs := [][2]string{
		{"hello", "helo"},
		{"golang", "goland"},
		{"abc", "xyz"},
		{"", "foo"},
		{"", ""},
		{"test", "test"},
	}
	for _, p := range pairs {
		a, b := p[0], p[1]
		ab := Similarity(a, b)
		ba := Similarity(b, a)
		if fmt.Sprintf("%.9f", ab) != fmt.Sprintf("%.9f", ba) {
			t.Errorf("Similarity(%q,%q)=%.9f != Similarity(%q,%q)=%.9f — not symmetric",
				a, b, ab, b, a, ba)
		}
	}
}

// TestSimilaritySelfIsMaximal checks that Similarity(a,a) >= Similarity(a,b)
// for any b. An identical word must be at least as similar as any other.
func TestSimilaritySelfIsMaximal(t *testing.T) {
	words := []string{"apple", "application", "ap", "a", "golang", "go", "test", ""}
	for _, a := range words {
		selfScore := Similarity(a, a)
		for _, b := range words {
			score := Similarity(a, b)
			if score > selfScore+1e-9 {
				t.Errorf("Similarity(%q,%q)=%.9f > Similarity(%q,%q)=%.9f — self not maximal",
					a, b, score, a, a, selfScore)
			}
		}
	}
}

// TestSimilarityDeterministic checks that repeated calls with the same
// arguments always return the same value.
func TestSimilarityDeterministic(t *testing.T) {
	pairs := [][2]string{
		{"hello", "world"},
		{"foo", "bar"},
		{"abc", "abcd"},
	}
	for _, p := range pairs {
		first := Similarity(p[0], p[1])
		for i := 0; i < 10; i++ {
			got := Similarity(p[0], p[1])
			if got != first {
				t.Errorf("Similarity(%q,%q) returned %.9f on call %d, want %.9f",
					p[0], p[1], got, i+1, first)
			}
		}
	}
}

// TestSuggestConsistentWithSimilarity is a differential test: for each result
// returned by Suggest, every word NOT in the result but in the vocabulary must
// have a Similarity score no greater than the minimum score in the result set
// (allowing a small epsilon for near-tie handling). This directly validates the
// contract stated in the documentation.
func TestSuggestConsistentWithSimilarity(t *testing.T) {
	words := []string{
		"cat", "bat", "hat", "rat", "sat", "fat",
		"dog", "fog", "hog", "log", "bog",
		"fish", "dish", "wish",
	}
	idx := New(words)
	const k = 5
	queries := []string{"cat", "dog", "fish", "xyz", "c"}

	for _, q := range queries {
		results := idx.Suggest(q, k)
		if len(results) == 0 {
			continue
		}

		// Find the minimum similarity score in the returned set.
		minScore := Similarity(q, results[0])
		for _, r := range results[1:] {
			s := Similarity(q, r)
			if s < minScore {
				minScore = s
			}
		}

		resultSet := toSet(results)
		// Every word outside the result must score <= minScore (with a small
		// epsilon for legitimate near-ties).
		const epsilon = 1e-9
		for _, w := range words {
			if resultSet[w] {
				continue
			}
			score := Similarity(q, w)
			if score > minScore+epsilon {
				t.Errorf("Suggest(%q, %d): omitted word %q (score %.6f) scores higher than min result score %.6f",
					q, k, w, score, minScore)
			}
		}
	}
}

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------

func toSet(words []string) map[string]bool {
	m := make(map[string]bool, len(words))
	for _, w := range words {
		m[w] = true
	}
	return m
}

func averageSimilarity(q string, words []string) float64 {
	if len(words) == 0 {
		return 0
	}
	sum := 0.0
	for _, w := range words {
		sum += Similarity(q, w)
	}
	return sum / float64(len(words))
}

// makeVocab generates n random lowercase words of length 3–8 using rng.
func makeVocab(rng *rand.Rand, n int) []string {
	const letters = "abcdefghijklmnopqrstuvwxyz"
	seen := make(map[string]bool, n)
	vocab := make([]string, 0, n)
	for len(vocab) < n {
		length := 3 + rng.Intn(6)
		b := make([]byte, length)
		for i := range b {
			b[i] = letters[rng.Intn(len(letters))]
		}
		w := string(b)
		if !seen[w] {
			seen[w] = true
			vocab = append(vocab, w)
		}
	}
	return vocab
}

// mutate introduces a small random edit (substitution or deletion) to a word
// so that fuzzy-match paths are exercised, while keeping the result close.
func mutate(rng *rand.Rand, word string) string {
	if len(word) == 0 {
		return word
	}
	switch rng.Intn(3) {
	case 0:
		// substitution at a random position
		idx := rng.Intn(len(word))
		b := []byte(word)
		b[idx] = 'a' + byte(rng.Intn(26))
		return string(b)
	case 1:
		// deletion of a random character
		if len(word) <= 1 {
			return word
		}
		idx := rng.Intn(len(word))
		return word[:idx] + word[idx+1:]
	default:
		// no mutation — query is exact
		return strings.Clone(word)
	}
}
