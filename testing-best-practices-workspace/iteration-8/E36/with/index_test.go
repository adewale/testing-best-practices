package index

import (
	"math/rand"
	"testing"
)

// TestRecallAgainstBruteForce tests the approximate top-k retriever against
// the exact brute-force implementation using a statistical recall threshold.
// Seed is pinned so "approximate" never means "flaky."
func TestRecallAgainstBruteForce(t *testing.T) {
	const seed = 42
	const n = 5000
	const dim = 64
	const k = 20
	const recallThreshold = 0.80

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	approx := toSet(idx.Query(q, k))
	exact := toSet(bruteForceTopK(vecs, q, k))

	overlap := 0
	for id := range approx {
		if exact[id] {
			overlap++
		}
	}

	recall := float64(overlap) / float64(k)
	if recall < recallThreshold {
		t.Errorf("recall %.2f is below threshold %.2f (seed=%d, n=%d, dim=%d, k=%d)",
			recall, recallThreshold, seed, n, dim, k)
	}
}

// TestRecallMultipleQueries runs several independent queries and requires that
// the average recall meets the threshold, making the test more robust than a
// single-query check.
func TestRecallMultipleQueries(t *testing.T) {
	const seed = 99
	const n = 3000
	const dim = 32
	const k = 10
	const numQueries = 20
	const recallThreshold = 0.80

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)

	totalOverlap := 0
	for i := 0; i < numQueries; i++ {
		q := randomVector(rng, dim)
		approx := toSet(idx.Query(q, k))
		exact := toSet(bruteForceTopK(vecs, q, k))

		for id := range approx {
			if exact[id] {
				totalOverlap++
			}
		}
	}

	avgRecall := float64(totalOverlap) / float64(numQueries*k)
	if avgRecall < recallThreshold {
		t.Errorf("average recall %.2f across %d queries is below threshold %.2f (seed=%d)",
			avgRecall, numQueries, recallThreshold, seed)
	}
}

// TestQueryReturnsExactlyKResults verifies that Query always returns exactly k
// indices when the index has at least k vectors.
func TestQueryReturnsExactlyKResults(t *testing.T) {
	const seed = 7
	const n = 200
	const dim = 16

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	for _, k := range []int{1, 5, 10, 50, 100} {
		results := idx.Query(q, k)
		if len(results) != k {
			t.Errorf("Query(q, %d) returned %d results, want %d", k, len(results), k)
		}
	}
}

// TestQueryResultsAreValidIndices verifies that every returned index is within
// the valid range [0, n).
func TestQueryResultsAreValidIndices(t *testing.T) {
	const seed = 13
	const n = 100
	const dim = 8
	const k = 20

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	results := idx.Query(q, k)
	for _, id := range results {
		if id < 0 || id >= n {
			t.Errorf("Query returned index %d, which is out of range [0, %d)", id, n)
		}
	}
}

// TestQueryResultsAreUnique verifies that Query does not return duplicate
// indices.
func TestQueryResultsAreUnique(t *testing.T) {
	const seed = 21
	const n = 500
	const dim = 32
	const k = 50

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	results := idx.Query(q, k)
	seen := toSet(results)
	if len(seen) != len(results) {
		t.Errorf("Query returned %d results but only %d are unique (duplicates present)",
			len(results), len(seen))
	}
}

// TestQueryKEqualsN verifies correctness when k equals the total number of
// vectors — the result set must be the full index (all indices present).
func TestQueryKEqualsN(t *testing.T) {
	const seed = 55
	const n = 50
	const dim = 8

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	results := idx.Query(q, n)
	if len(results) != n {
		t.Fatalf("Query(q, n=%d) returned %d results, want %d", n, len(results), n)
	}

	resultSet := toSet(results)
	for i := 0; i < n; i++ {
		if !resultSet[i] {
			t.Errorf("Query(q, n) is missing index %d", i)
		}
	}
}

// TestQueryKEqualOne verifies that a query for the single nearest neighbor
// returns exactly one result that is among the top candidates from the exact
// brute force search.
func TestQueryKEqualOne(t *testing.T) {
	const seed = 3
	const n = 1000
	const dim = 16
	// We allow the single returned result to be within the top-5 exact results
	// to accommodate the approximate nature of the retriever.
	const topCandidates = 5

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	results := idx.Query(q, 1)
	if len(results) != 1 {
		t.Fatalf("Query(q, 1) returned %d results, want 1", len(results))
	}

	exactTop := toSet(bruteForceTopK(vecs, q, topCandidates))
	if !exactTop[results[0]] {
		t.Errorf("Query(q, 1) returned index %d which is not in the exact top-%d results",
			results[0], topCandidates)
	}
}

// TestRecallHighDimension verifies recall holds for higher-dimensional vectors,
// where approximate methods can degrade.
func TestRecallHighDimension(t *testing.T) {
	const seed = 77
	const n = 2000
	const dim = 256
	const k = 10
	const recallThreshold = 0.70 // slightly relaxed for high-dim

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	approx := toSet(idx.Query(q, k))
	exact := toSet(bruteForceTopK(vecs, q, k))

	overlap := 0
	for id := range approx {
		if exact[id] {
			overlap++
		}
	}

	recall := float64(overlap) / float64(k)
	if recall < recallThreshold {
		t.Errorf("high-dim recall %.2f is below threshold %.2f (seed=%d, n=%d, dim=%d, k=%d)",
			recall, recallThreshold, seed, n, dim, k)
	}
}

// TestRecallSmallCorpus verifies that even with a small corpus the retriever
// returns sensible results.
func TestRecallSmallCorpus(t *testing.T) {
	const seed = 88
	const n = 20
	const dim = 8
	const k = 5
	const recallThreshold = 0.80

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, n, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	approx := toSet(idx.Query(q, k))
	exact := toSet(bruteForceTopK(vecs, q, k))

	overlap := 0
	for id := range approx {
		if exact[id] {
			overlap++
		}
	}

	recall := float64(overlap) / float64(k)
	if recall < recallThreshold {
		t.Errorf("small-corpus recall %.2f is below threshold %.2f (seed=%d, n=%d, dim=%d, k=%d)",
			recall, recallThreshold, seed, n, dim, k)
	}
}

// TestDifferentSeedsGiveConsistentRecall checks that recall is consistently
// acceptable across multiple different random seeds, ruling out a lucky single
// seed masking a regression.
func TestDifferentSeedsGiveConsistentRecall(t *testing.T) {
	const n = 1000
	const dim = 32
	const k = 20
	const recallThreshold = 0.80

	seeds := []int64{11, 22, 33, 44, 55}

	for _, seed := range seeds {
		seed := seed // capture range variable
		t.Run("", func(t *testing.T) {
			rng := rand.New(rand.NewSource(seed))
			vecs := randomVectors(rng, n, dim)
			idx := New(vecs)
			q := randomVector(rng, dim)

			approx := toSet(idx.Query(q, k))
			exact := toSet(bruteForceTopK(vecs, q, k))

			overlap := 0
			for id := range approx {
				if exact[id] {
					overlap++
				}
			}

			recall := float64(overlap) / float64(k)
			if recall < recallThreshold {
				t.Errorf("recall %.2f is below threshold %.2f (seed=%d)", recall, recallThreshold, seed)
			}
		})
	}
}

// TestNewWithSingleVector verifies that the index can be constructed with a
// single vector and queried for k=1 without panicking or returning invalid data.
func TestNewWithSingleVector(t *testing.T) {
	const seed = 5
	const dim = 8

	rng := rand.New(rand.NewSource(seed))
	vecs := randomVectors(rng, 1, dim)
	idx := New(vecs)
	q := randomVector(rng, dim)

	results := idx.Query(q, 1)
	if len(results) != 1 {
		t.Fatalf("Query(q, 1) on single-vector index returned %d results, want 1", len(results))
	}
	if results[0] != 0 {
		t.Errorf("Query(q, 1) on single-vector index returned index %d, want 0", results[0])
	}
}
