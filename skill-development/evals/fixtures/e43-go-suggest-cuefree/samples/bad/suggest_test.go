package suggest

import (
	"reflect"
	"testing"
)

func TestSuggest(t *testing.T) {
	idx := New([]string{"hello", "help", "hell", "world"})
	got := idx.Suggest("helo", 3)
	if !reflect.DeepEqual(got, []string{"hello", "help", "hell"}) {
		t.Errorf("got %v", got)
	}
}
