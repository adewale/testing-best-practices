package index

import (
	"math/rand"
	"testing"
)

func TestRecallAgainstBruteForce(t *testing.T) {
	rng := rand.New(rand.NewSource(42))
	vecs := randomVectors(rng, 20000, 128)
	idx := New(vecs)
	q := randomVector(rng, 128)

	approx := toSet(idx.Query(q, 50))
	exact := toSet(bruteForceTopK(vecs, q, 50)) // the oracle

	hit := 0
	for id := range approx {
		if exact[id] {
			hit++
		}
	}
	recall := float64(hit) / 50.0
	if recall < 0.90 {
		t.Fatalf("recall %.2f below 0.90 threshold", recall)
	}
}
