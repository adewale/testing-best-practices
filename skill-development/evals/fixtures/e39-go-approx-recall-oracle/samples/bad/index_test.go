package index

import "testing"

func TestQueryReturnsK(t *testing.T) {
	idx := New(testVectors())
	if len(idx.Query(testVectors()[0], 5)) != 5 {
		t.Error("wrong length")
	}
}
