package reportfixture

import (
	"errors"
	"path/filepath"
	"testing"
)

type fakeNotifier struct { err error; calls []string }
func (f *fakeNotifier) Notify(path string) error { f.calls = append(f.calls, path); return f.err }

func TestWriteReportPropagatesNotifierFailure(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "report.txt")
	notifyErr := errors.New("notify failure")
	n := &fakeNotifier{err: notifyErr}
	err := WriteReport(path, "body", n)
	if !errors.Is(err, notifyErr) { t.Fatalf("err = %v, want notifier error", err) }
	if len(n.calls) != 1 { t.Fatalf("calls = %d, want 1", len(n.calls)) }
}
