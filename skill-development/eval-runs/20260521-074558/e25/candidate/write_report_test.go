package reports

import (
	"errors"
	"os"
	"path/filepath"
	"testing"
)

type fakeNotifier struct {
	paths []string
	err   error
}

func (f *fakeNotifier) Notify(reportPath string) error {
	f.paths = append(f.paths, reportPath)
	return f.err
}

func TestWriteReportWritesFileAndNotifies(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "daily.txt")
	reportBody := "orders=12\nrevenue=34.50\n"
	notifier := &fakeNotifier{}

	if err := WriteReport(reportPath, reportBody, notifier); err != nil {
		t.Fatalf("WriteReport() returned error: %v", err)
	}

	assertFileContent(t, reportPath, reportBody)
	assertNotifiedOnce(t, notifier, reportPath)
}

func TestWriteReportReturnsWriteErrorAndDoesNotNotify(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "report.txt")
	if err := os.Mkdir(reportPath, 0o755); err != nil {
		t.Fatalf("create directory at report path: %v", err)
	}
	notifier := &fakeNotifier{}

	err := WriteReport(reportPath, "body", notifier)
	if err == nil {
		t.Fatal("WriteReport() error = nil, want write error")
	}
	if len(notifier.paths) != 0 {
		t.Fatalf("notifier called on write failure with paths %v; want no calls", notifier.paths)
	}
}

func TestWriteReportReturnsNotifierErrorAfterWritingFile(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "daily.txt")
	reportBody := "inventory=7\n"
	notifyErr := errors.New("notifier unavailable")
	notifier := &fakeNotifier{err: notifyErr}

	err := WriteReport(reportPath, reportBody, notifier)
	if !errors.Is(err, notifyErr) {
		t.Fatalf("WriteReport() error = %v, want notifier error %v", err, notifyErr)
	}

	assertFileContent(t, reportPath, reportBody)
	assertNotifiedOnce(t, notifier, reportPath)
}

func assertFileContent(t *testing.T, path, want string) {
	t.Helper()
	got, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("ReadFile(%q): %v", path, err)
	}
	if string(got) != want {
		t.Fatalf("file content = %q, want %q", string(got), want)
	}
}

func assertNotifiedOnce(t *testing.T, notifier *fakeNotifier, wantPath string) {
	t.Helper()
	if len(notifier.paths) != 1 {
		t.Fatalf("notifier calls = %d (%v), want 1", len(notifier.paths), notifier.paths)
	}
	if notifier.paths[0] != wantPath {
		t.Fatalf("notifier path = %q, want %q", notifier.paths[0], wantPath)
	}
}
