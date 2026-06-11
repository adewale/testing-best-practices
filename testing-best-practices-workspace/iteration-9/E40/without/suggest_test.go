package suggest

import (
	"math/rand"
	"sort"
	"testing"
)

// shadowSuggest is a deliberately dumb reference implementation that is
// obviously correct: it scores every word with Similarity and picks the top k
// by sorting. It trades performance for transparent correctness and serves as
// the oracle for the optimised Index.
func shadowSuggest(words []string, q string, k int) []string {
	type scored struct {
		word  string
		score float64
	}
	results := make([]scored, len(words))
	for i, w := range words {
		results[i] = scored{w, Similarity(q, w)}
	}
	sort.SliceStable(results, func(i, j int) bool {
		return results[i].score > results[j].score
	})
	if k > len(results) {
		k = len(results)
	}
	out := make([]string, k)
	for i := range out {
		out[i] = results[i].word
	}
	return out
}

// similarityScore returns the Similarity value for a word as scored against q,
// used to check result invariants.
func similarityScore(q, w string) float64 {
	return Similarity(q, w)
}

// minScore returns the minimum Similarity score among a list of words against q.
func minScoreOf(q string, words []string) float64 {
	if len(words) == 0 {
		return 0
	}
	min := Similarity(q, words[0])
	for _, w := range words[1:] {
		if s := Similarity(q, w); s < min {
			min = s
		}
	}
	return min
}

// TestSimilarityReflexive checks that Similarity(a,a) is the maximum possible
// score — a word is always more similar to itself than to anything else.
func TestSimilarityReflexive(t *testing.T) {
	words := []string{"hello", "world", "foo", "bar", "testing", "go", "suggest"}
	for _, w := range words {
		self := Similarity(w, w)
		for _, other := range words {
			if other == w {
				continue
			}
			if s := Similarity(w, other); s > self {
				t.Errorf("Similarity(%q,%q)=%f > Similarity(%q,%q)=%f: self-similarity should be maximal",
					w, other, s, w, w, self)
			}
		}
	}
}

// TestSimilaritySymmetric checks that Similarity is symmetric: Similarity(a,b)
// == Similarity(b,a).
func TestSimilaritySymmetric(t *testing.T) {
	pairs := [][2]string{
		{"hello", "hell"},
		{"kitten", "sitting"},
		{"abc", "xyz"},
		{"foo", "foo"},
		{"", "bar"},
		{"bar", ""},
		{"", ""},
		{"go", "golang"},
		{"test", "testing"},
	}
	for _, p := range pairs {
		ab := Similarity(p[0], p[1])
		ba := Similarity(p[1], p[0])
		if ab != ba {
			t.Errorf("Similarity(%q,%q)=%f != Similarity(%q,%q)=%f: expected symmetry",
				p[0], p[1], ab, p[1], p[0], ba)
		}
	}
}

// TestSimilarityNonNegative checks that Similarity never returns a negative value.
func TestSimilarityNonNegative(t *testing.T) {
	rng := rand.New(rand.NewSource(42))
	alphabet := []rune("abcdefghijklmnopqrstuvwxyz")
	for i := 0; i < 500; i++ {
		a := randomWord(rng, alphabet, 0, 12)
		b := randomWord(rng, alphabet, 0, 12)
		if s := Similarity(a, b); s < 0 {
			t.Errorf("Similarity(%q,%q)=%f: negative score", a, b, s)
		}
	}
}

// TestSimilarityDeterministic checks that repeated calls with the same arguments
// return the same value.
func TestSimilarityDeterministic(t *testing.T) {
	pairs := [][2]string{
		{"hello", "helo"},
		{"suggest", "suggestion"},
		{"foo", "bar"},
		{"", ""},
	}
	for _, p := range pairs {
		first := Similarity(p[0], p[1])
		for i := 0; i < 5; i++ {
			if s := Similarity(p[0], p[1]); s != first {
				t.Errorf("Similarity(%q,%q) is non-deterministic: got %f then %f",
					p[0], p[1], first, s)
			}
		}
	}
}

// TestSuggestLengthAtMostK checks that Suggest never returns more than k items.
func TestSuggestLengthAtMostK(t *testing.T) {
	words := []string{"apple", "application", "apply", "apt", "banana", "band", "bandana"}
	idx := New(words)
	cases := []struct{ q string; k int }{
		{"app", 3},
		{"app", 0},
		{"app", 10},
		{"app", 1},
		{"zzz", 5},
	}
	for _, tc := range cases {
		got := idx.Suggest(tc.q, tc.k)
		if len(got) > tc.k {
			t.Errorf("Suggest(%q,%d) returned %d results, want at most %d",
				tc.q, tc.k, len(got), tc.k)
		}
	}
}

// TestSuggestLengthAtMostVocab checks that Suggest never returns more words than
// are in the vocabulary.
func TestSuggestLengthAtMostVocab(t *testing.T) {
	words := []string{"cat", "car", "card"}
	idx := New(words)
	got := idx.Suggest("ca", 100)
	if len(got) > len(words) {
		t.Errorf("Suggest returned %d results but vocabulary has only %d words",
			len(got), len(words))
	}
}

// TestSuggestZeroK checks that Suggest with k=0 returns an empty slice.
func TestSuggestZeroK(t *testing.T) {
	idx := New([]string{"hello", "world"})
	got := idx.Suggest("hello", 0)
	if len(got) != 0 {
		t.Errorf("Suggest(q,0) returned %v, want empty slice", got)
	}
}

// TestSuggestEmptyVocab checks that Suggest on an empty index returns an empty
// slice regardless of k.
func TestSuggestEmptyVocab(t *testing.T) {
	idx := New([]string{})
	got := idx.Suggest("anything", 5)
	if len(got) != 0 {
		t.Errorf("Suggest on empty vocab returned %v, want empty", got)
	}
}

// TestSuggestResultsAreFromVocab checks that every word returned by Suggest
// actually belongs to the vocabulary used to build the index.
func TestSuggestResultsAreFromVocab(t *testing.T) {
	words := []string{"alpha", "beta", "gamma", "delta", "epsilon"}
	vocabSet := make(map[string]bool, len(words))
	for _, w := range words {
		vocabSet[w] = true
	}
	idx := New(words)
	queries := []string{"alph", "bet", "zzz", "", "gamma"}
	for _, q := range queries {
		for k := 1; k <= len(words)+2; k++ {
			got := idx.Suggest(q, k)
			for _, r := range got {
				if !vocabSet[r] {
					t.Errorf("Suggest(%q,%d) returned %q which is not in vocab", q, k, r)
				}
			}
		}
	}
}

// TestSuggestNoDuplicates checks that Suggest never returns the same word twice.
func TestSuggestNoDuplicates(t *testing.T) {
	words := []string{"cat", "car", "card", "care", "core", "bore"}
	idx := New(words)
	queries := []string{"car", "ca", "cor", "x"}
	for _, q := range queries {
		got := idx.Suggest(q, len(words))
		seen := make(map[string]bool)
		for _, w := range got {
			if seen[w] {
				t.Errorf("Suggest(%q,%d) returned duplicate word %q in %v", q, len(words), w, got)
			}
			seen[w] = true
		}
	}
}

// TestSuggestResultsOrderedBySimilarity uses Similarity as the oracle to check
// that results are returned in non-increasing similarity order. This is the key
// differential test: the exported, deterministic Similarity function IS the
// specification for the ordering.
func TestSuggestResultsOrderedBySimilarity(t *testing.T) {
	words := []string{"kitten", "sitting", "kitchen", "mitten", "bitten", "written", "rotten", "button"}
	idx := New(words)
	queries := []string{"kitten", "kiten", "sit", "mitt", "xyz"}
	for _, q := range queries {
		got := idx.Suggest(q, len(words))
		for i := 1; i < len(got); i++ {
			si := Similarity(q, got[i-1])
			sj := Similarity(q, got[i])
			if sj > si {
				t.Errorf("Suggest(%q): result[%d]=%q (sim=%f) has higher similarity than result[%d]=%q (sim=%f); want non-increasing order",
					q, i, got[i], sj, i-1, got[i-1], si)
			}
		}
	}
}

// TestSuggestTopKAreBestK uses the shadow model as oracle: the k words returned
// by Suggest must be exactly the k words with the highest Similarity scores
// (accounting for near-tie ambiguity at the boundary).
//
// The documented behaviour is that near-ties at the k-th boundary may differ
// between builds, so we verify the weaker but still meaningful property:
// every word returned by Suggest has similarity >= the minimum similarity of
// the shadow model's top-k results, and every word NOT returned (from the same
// vocabulary) that the shadow model puts in its top-k has similarity equal to
// that boundary score (i.e., it's a genuine tie at the cut-off).
func TestSuggestTopKAreBestK(t *testing.T) {
	words := []string{
		"hello", "hell", "help", "helm", "held", "heal",
		"hear", "heat", "heap", "hero", "herd", "herb",
	}
	idx := New(words)
	queries := []string{"hell", "help", "her", "helo", "xyz"}

	for _, q := range queries {
		for _, k := range []int{1, 3, 5, len(words)} {
			got := idx.Suggest(q, k)
			shadow := shadowSuggest(words, q, k)

			if len(got) != len(shadow) {
				t.Errorf("Suggest(%q,%d) returned %d results, shadow returned %d",
					q, k, len(got), len(shadow))
				continue
			}

			// The minimum similarity in the shadow top-k is the threshold.
			threshold := minScoreOf(q, shadow)

			// Every word Suggest returned must score >= threshold.
			for _, w := range got {
				if s := Similarity(q, w); s < threshold {
					t.Errorf("Suggest(%q,%d) returned %q with similarity %f, but shadow threshold is %f",
						q, k, w, s, threshold)
				}
			}

			// Every word in the shadow top-k must score >= threshold (sanity).
			// Also, words Suggest returned must collectively have the same total
			// similarity mass as shadow — same multiset of scores when all scores
			// are above the threshold.
			shadowScores := make([]float64, len(shadow))
			for i, w := range shadow {
				shadowScores[i] = Similarity(q, w)
			}
			gotScores := make([]float64, len(got))
			for i, w := range got {
				gotScores[i] = Similarity(q, w)
			}
			sort.Float64s(shadowScores)
			sort.Float64s(gotScores)
			// For scores strictly above the boundary, they must match exactly.
			for i := range gotScores {
				gs := gotScores[i]
				ss := shadowScores[i]
				// A near-tie is when both are equal to the threshold; that is
				// the documented ambiguous zone. Outside the tie zone they must agree.
				if gs != threshold && ss != threshold && gs != ss {
					t.Errorf("Suggest(%q,%d): score mismatch at position %d: got %f, shadow %f",
						q, k, i, gs, ss)
				}
			}
		}
	}
}

// TestSuggestExactMatchIsFirst checks the intuitive invariant that when the
// query is itself in the vocabulary, it must appear first (highest self-similarity).
func TestSuggestExactMatchIsFirst(t *testing.T) {
	words := []string{"cat", "car", "card", "care", "bat", "bar"}
	idx := New(words)
	for _, q := range words {
		got := idx.Suggest(q, len(words))
		if len(got) == 0 {
			t.Errorf("Suggest(%q) returned no results", q)
			continue
		}
		if got[0] != q {
			t.Errorf("Suggest(%q): expected exact match first, got %q (sim=%f vs self sim=%f)",
				q, got[0], Similarity(q, got[0]), Similarity(q, q))
		}
	}
}

// TestSuggestAgainstShadowModelFuzz drives New+Suggest and shadowSuggest with
// the same randomly generated vocabularies and queries, using Similarity as the
// agreed-upon scoring function. The seed is fixed so any failure is reproducible.
func TestSuggestAgainstShadowModelFuzz(t *testing.T) {
	rng := rand.New(rand.NewSource(2024_06_10))
	alphabet := []rune("abcdefghijklmnopqrstuvwxyz")

	for trial := 0; trial < 100; trial++ {
		// Build a random vocabulary of 5–20 words.
		vocabSize := 5 + rng.Intn(16)
		words := make([]string, vocabSize)
		for i := range words {
			words[i] = randomWord(rng, alphabet, 1, 8)
		}

		idx := New(words)
		q := randomWord(rng, alphabet, 1, 8)
		k := 1 + rng.Intn(vocabSize)

		got := idx.Suggest(q, k)
		shadow := shadowSuggest(words, q, k)

		if len(got) != len(shadow) {
			t.Errorf("trial %d: Suggest(%q,%d) len=%d shadow len=%d; vocab=%v",
				trial, q, k, len(got), len(shadow), words)
			continue
		}

		// Every result must come from the vocabulary.
		vocabSet := make(map[string]bool, len(words))
		for _, w := range words {
			vocabSet[w] = true
		}
		for _, w := range got {
			if !vocabSet[w] {
				t.Errorf("trial %d: Suggest returned %q not in vocab", trial, w)
			}
		}

		// Results must be in non-increasing similarity order.
		for i := 1; i < len(got); i++ {
			si := Similarity(q, got[i-1])
			sj := Similarity(q, got[i])
			if sj > si {
				t.Errorf("trial %d: Suggest(%q,%d) result not sorted: [%d]=%q sim=%f > [%d]=%q sim=%f",
					trial, q, k, i, got[i], sj, i-1, got[i-1], si)
			}
		}

		// The set of similarities of returned words must be >= the shadow threshold.
		if len(shadow) > 0 {
			threshold := minScoreOf(q, shadow)
			for _, w := range got {
				if s := Similarity(q, w); s < threshold {
					t.Errorf("trial %d: Suggest(%q,%d) returned %q sim=%f below shadow threshold %f",
						trial, q, k, w, s, threshold)
				}
			}
		}
	}
}

// TestNewDoesNotMutateInput checks that constructing an Index does not modify
// the original words slice passed to New.
func TestNewDoesNotMutateInput(t *testing.T) {
	original := []string{"delta", "alpha", "charlie", "bravo"}
	snapshot := make([]string, len(original))
	copy(snapshot, original)

	New(original)

	for i, w := range original {
		if w != snapshot[i] {
			t.Errorf("New mutated input slice: index %d changed from %q to %q", i, snapshot[i], w)
		}
	}
}

// TestSuggestStableAcrossMultipleIndexes checks that two Index instances built
// from the same vocabulary return results with the same similarity scores for
// the same query (even if near-tie ordering may vary, the score distribution
// must be identical).
func TestSuggestStableAcrossMultipleIndexes(t *testing.T) {
	words := []string{"run", "ran", "runner", "running", "rung", "rang", "rank"}
	idx1 := New(words)
	idx2 := New(words)
	queries := []string{"run", "ran", "rin", "xyz"}
	for _, q := range queries {
		k := len(words)
		got1 := idx1.Suggest(q, k)
		got2 := idx2.Suggest(q, k)
		scores1 := make([]float64, len(got1))
		scores2 := make([]float64, len(got2))
		for i, w := range got1 {
			scores1[i] = Similarity(q, w)
		}
		for i, w := range got2 {
			scores2[i] = Similarity(q, w)
		}
		sort.Float64s(scores1)
		sort.Float64s(scores2)
		if len(scores1) != len(scores2) {
			t.Errorf("Two indexes returned different result counts for Suggest(%q,%d)", q, k)
			continue
		}
		for i := range scores1 {
			if scores1[i] != scores2[i] {
				t.Errorf("Suggest(%q,%d): score distributions differ between two equal indexes at position %d: %f vs %f",
					q, k, i, scores1[i], scores2[i])
			}
		}
	}
}

// randomWord generates a random word of length in [minLen, maxLen] from alphabet.
func randomWord(rng *rand.Rand, alphabet []rune, minLen, maxLen int) string {
	n := minLen
	if maxLen > minLen {
		n += rng.Intn(maxLen - minLen + 1)
	}
	runes := make([]rune, n)
	for i := range runes {
		runes[i] = alphabet[rng.Intn(len(alphabet))]
	}
	return string(runes)
}
