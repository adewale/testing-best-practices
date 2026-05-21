package reports

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type fakeNotifier struct {
	err   error
	calls []string
}

func (f *fakeNotifier) Notify(reportPath string) error {
	f.calls = append(f.calls, reportPath)
	return f.err
}

func TestWriteReportWritesFileAndNotifies(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "daily-report.txt")
	body := []byte("status: green\nitems: 3\n")
	notifier := &fakeNotifier{}

	err := WriteReport(reportPath, body, notifier)
	if err != nil {
		t.Fatalf("WriteReport() error = %v, want nil", err)
	}

	got, err := os.ReadFile(reportPath)
	if err != nil {
		t.Fatalf("read written report: %v", err)
	}
	if string(got) != string(body) {
		t.Errorf("written report = %q, want %q", got, body)
	}
	if len(notifier.calls) != 1 {
		t.Fatalf("notifier calls = %d, want 1", len(notifier.calls))
	}
	if notifier.calls[0] != reportPath {
		t.Errorf("notified path = %q, want %q", notifier.calls[0], reportPath)
	}
}

func TestWriteReportReturnsWriteErrorAndDoesNotNotify(t *testing.T) {
	dir := t.TempDir()
	parentFile := filepath.Join(dir, "not-a-directory")
	if err := os.WriteFile(parentFile, []byte("blocks child writes"), 0o600); err != nil {
		t.Fatalf("create parent file: %v", err)
	}
	reportPath := filepath.Join(parentFile, "report.txt")
	notifier := &fakeNotifier{}

	err := WriteReport(reportPath, []byte("unwritten report"), notifier)
	if err == nil {
		t.Fatal("WriteReport() error = nil, want write failure")
	}
	if !strings.Contains(strings.ToLower(err.Error()), "write") && !strings.Contains(strings.ToLower(err.Error()), "not a directory") {
		t.Errorf("WriteReport() error = %v, want write/not-a-directory context", err)
	}
	if len(notifier.calls) != 0 {
		t.Errorf("notifier calls = %d, want 0 after write failure", len(notifier.calls))
	}
	if _, statErr := os.Stat(reportPath); statErr == nil {
		t.Errorf("report file %q exists after write failure", reportPath)
	}
}

func TestWriteReportReturnsNotifierErrorAfterWritingFile(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "notify-fails.txt")
	body := []byte("report was persisted before notify failed\n")
	wantErr := errors.New("notifier unavailable")
	notifier := &fakeNotifier{err: wantErr}

	err := WriteReport(reportPath, body, notifier)
	if !errors.Is(err, wantErr) {
		t.Fatalf("WriteReport() error = %v, want notifier error %v", err, wantErr)
	}

	got, readErr := os.ReadFile(reportPath)
	if readErr != nil {
		t.Fatalf("read report after notifier failure: %v", readErr)
	}
	if string(got) != string(body) {
		t.Errorf("written report = %q, want %q", got, body)
	}
	if len(notifier.calls) != 1 {
		t.Fatalf("notifier calls = %d, want 1", len(notifier.calls))
	}
	if notifier.calls[0] != reportPath {
		t.Errorf("notified path = %q, want %q", notifier.calls[0], reportPath)
	}
}
