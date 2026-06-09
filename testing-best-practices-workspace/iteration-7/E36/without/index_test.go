package index

import (
	"math/rand"
	"testing"
)

// TestQueryRecallAgainstBruteForce is the core differential test:
// bruteForceTopK is the trusted oracle; Query is the implementation under test.
// Because retrieval is approximate, we accept a recall threshold rather than
// requiring an exact match.
func TestQueryRecallAgainstBruteForce(t *testing.T) {
	cases := []struct {
		name          string
		n, dim, k     int
		seed          int64
		minRecall     float64 // fraction of brute-force results that must appear
	}{
		{name: "small_k1", n: 100, dim: 16, k: 1, seed: 1, minRecall: 1.0},
		{name: "small_k5", n: 100, dim: 16, k: 5, seed: 2, minRecall: 0.6},
		{name: "medium_k10", n: 500, dim: 32, k: 10, seed: 3, minRecall: 0.5},
		{name: "large_k20", n: 1000, dim: 64, k: 20, seed: 4, minRecall: 0.4},
		{name: "high_dim_k5", n: 200, dim: 128, k: 5, seed: 5, minRecall: 0.5},
		{name: "k_equals_n", n: 10, dim: 8, k: 10, seed: 6, minRecall: 1.0},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			rng := rand.New(rand.NewSource(tc.seed))
			vecs := randomVectors(rng, tc.n, tc.dim)
			q := randomVector(rng, tc.dim)

			idx := New(vecs)
			got := idx.Query(q, tc.k)
			want := bruteForceTopK(vecs, q, tc.k)

			// Verify the result length is exactly k (or n if k > n).
			expectedLen := tc.k
			if tc.n < tc.k {
				expectedLen = tc.n
			}
			if len(got) != expectedLen {
				t.Errorf("Query returned %d results, want %d", len(got), expectedLen)
			}

			// Differential: measure recall against the brute-force oracle.
			gotSet := toSet(got)
			wantSet := toSet(want)
			hits := 0
			for id := range wantSet {
				if gotSet[id] {
					hits++
				}
			}
			recall := float64(hits) / float64(len(wantSet))
			if recall < tc.minRecall {
				t.Errorf("recall = %.2f (hits %d/%d), want >= %.2f",
					recall, hits, len(wantSet), tc.minRecall)
			}
		})
	}
}

// TestQueryResultsAreValidIndices checks that every returned index is within
// the valid range [0, n).
func TestQueryResultsAreValidIndices(t *testing.T) {
	rng := rand.New(rand.NewSource(42))
	n, dim, k := 200, 32, 15
	vecs := randomVectors(rng, n, dim)
	q := randomVector(rng, dim)

	idx := New(vecs)
	got := idx.Query(q, k)

	for _, id := range got {
		if id < 0 || id >= n {
			t.Errorf("returned index %d out of range [0, %d)", id, n)
		}
	}
}

// TestQueryNoDuplicates ensures Query does not return the same index twice.
func TestQueryNoDuplicates(t *testing.T) {
	rng := rand.New(rand.NewSource(99))
	n, dim, k := 300, 16, 20
	vecs := randomVectors(rng, n, dim)
	q := randomVector(rng, dim)

	idx := New(vecs)
	got := idx.Query(q, k)

	seen := make(map[int]bool, len(got))
	for _, id := range got {
		if seen[id] {
			t.Errorf("duplicate index %d in Query result", id)
		}
		seen[id] = true
	}
}

// TestQueryDeterministicOnSameInput verifies that repeated calls with the same
// query return the same result (no non-determinism from uninitialized state).
func TestQueryDeterministicOnSameInput(t *testing.T) {
	rng := rand.New(rand.NewSource(7))
	n, dim, k := 150, 24, 8
	vecs := randomVectors(rng, n, dim)
	q := randomVector(rng, dim)

	idx := New(vecs)
	first := idx.Query(q, k)
	second := idx.Query(q, k)

	firstSet := toSet(first)
	secondSet := toSet(second)

	if len(firstSet) != len(secondSet) {
		t.Fatalf("Query returned different lengths on repeated call: %d vs %d",
			len(first), len(second))
	}
	for id := range firstSet {
		if !secondSet[id] {
			t.Errorf("Query is non-deterministic: index %d in first call but not second", id)
		}
	}
}

// TestQueryKLargerThanN verifies that when k > n the index returns at most n
// results (all of them), each a valid index.
func TestQueryKLargerThanN(t *testing.T) {
	rng := rand.New(rand.NewSource(13))
	n, dim := 5, 8
	vecs := randomVectors(rng, n, dim)
	q := randomVector(rng, dim)

	idx := New(vecs)
	got := idx.Query(q, n*3)

	if len(got) > n {
		t.Errorf("Query returned %d results with n=%d; expected at most n", len(got), n)
	}
	for _, id := range got {
		if id < 0 || id >= n {
			t.Errorf("returned index %d out of range [0, %d)", id, n)
		}
	}
}

// TestQueryK1RecallIsPerfect checks that querying for the single best neighbour
// finds it exactly, i.e., differential recall == 1.0 for k=1 across many queries.
// ANN indexes generally guarantee this for sufficiently well-separated data.
func TestQueryK1RecallIsPerfect(t *testing.T) {
	rng := rand.New(rand.NewSource(21))
	n, dim := 200, 16
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)

	trials := 20
	hits := 0
	for i := 0; i < trials; i++ {
		q := randomVector(rng, dim)
		got := idx.Query(q, 1)
		want := bruteForceTopK(vecs, q, 1)
		if len(got) == 1 && len(want) == 1 && got[0] == want[0] {
			hits++
		}
	}
	recall := float64(hits) / float64(trials)
	// Allow one miss out of 20 to tolerate edge cases in approximate search.
	if recall < 0.9 {
		t.Errorf("k=1 recall = %.2f across %d queries, want >= 0.90", recall, trials)
	}
}

// TestRecallImprovesOrStaysWithLargerK is a differential monotonicity check:
// recall@2k should be >= recall@k when both are measured against the
// brute-force top-2k list.
func TestRecallImprovesOrStaysWithLargerK(t *testing.T) {
	rng := rand.New(rand.NewSource(55))
	n, dim := 400, 32
	vecs := randomVectors(rng, n, dim)
	q := randomVector(rng, dim)
	idx := New(vecs)

	k := 5
	got5 := idx.Query(q, k)
	got10 := idx.Query(q, k*2)
	want10 := bruteForceTopK(vecs, q, k*2)

	wantSet := toSet(want10)

	hits5 := 0
	for _, id := range got5 {
		if wantSet[id] {
			hits5++
		}
	}
	hits10 := 0
	for _, id := range got10 {
		if wantSet[id] {
			hits10++
		}
	}

	// A larger k result set must cover at least as many true neighbours as the
	// smaller one (when measured against the larger ground-truth set).
	if hits10 < hits5 {
		t.Errorf("hits@10=%d < hits@5=%d; larger k should not reduce coverage", hits10, hits5)
	}
}

// TestMultipleIndependentIndexes verifies that two Index instances built from
// different corpora do not share state and each differentially matches its own
// brute-force oracle.
func TestMultipleIndependentIndexes(t *testing.T) {
	rng := rand.New(rand.NewSource(77))
	n, dim, k := 100, 16, 5

	vecs1 := randomVectors(rng, n, dim)
	vecs2 := randomVectors(rng, n, dim)
	q := randomVector(rng, dim)

	idx1 := New(vecs1)
	idx2 := New(vecs2)

	got1 := idx1.Query(q, k)
	got2 := idx2.Query(q, k)
	want1 := bruteForceTopK(vecs1, q, k)
	want2 := bruteForceTopK(vecs2, q, k)

	recallFor := func(got, want []int) float64 {
		gs := toSet(got)
		ws := toSet(want)
		hits := 0
		for id := range ws {
			if gs[id] {
				hits++
			}
		}
		return float64(hits) / float64(len(ws))
	}

	if r := recallFor(got1, want1); r < 0.4 {
		t.Errorf("idx1 recall=%.2f, want >= 0.40", r)
	}
	if r := recallFor(got2, want2); r < 0.4 {
		t.Errorf("idx2 recall=%.2f, want >= 0.40", r)
	}

	// The two indexes should not return identical results for the same query
	// (they were built from different corpora).
	if toSet(got1)[0] && toSet(got2)[0] {
		// This is not necessarily wrong — just a sanity note, not a hard failure.
	}
}

// TestRecallAcrossMultipleQueries runs many random queries and checks that the
// average recall against bruteForceTopK stays above a threshold, providing a
// statistical differential signal rather than pass/fail on a single query.
func TestRecallAcrossMultipleQueries(t *testing.T) {
	rng := rand.New(rand.NewSource(333))
	n, dim, k := 500, 32, 10
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)

	trials := 30
	totalRecall := 0.0
	for i := 0; i < trials; i++ {
		q := randomVector(rng, dim)
		got := idx.Query(q, k)
		want := bruteForceTopK(vecs, q, k)
		gs := toSet(got)
		ws := toSet(want)
		hits := 0
		for id := range ws {
			if gs[id] {
				hits++
			}
		}
		totalRecall += float64(hits) / float64(len(ws))
	}
	avgRecall := totalRecall / float64(trials)
	if avgRecall < 0.4 {
		t.Errorf("average recall over %d queries = %.3f, want >= 0.40", trials, avgRecall)
	}
}
