package reports

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type recordingNotifier struct {
	err   error
	calls []string
}

func (n *recordingNotifier) Notify(reportPath string) error {
	n.calls = append(n.calls, reportPath)
	return n.err
}

func TestWriteReportWritesFileInTempDirAndNotifies(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "daily-report.txt")
	body := "Daily Report\norders=42\nstatus=green\n"
	notifier := &recordingNotifier{}

	err := WriteReport(reportPath, body, notifier)
	if err != nil {
		t.Fatalf("WriteReport() returned unexpected error: %v", err)
	}

	if filepath.Dir(reportPath) != dir {
		t.Fatalf("test report path escaped temp dir: got %q, want parent %q", reportPath, dir)
	}

	got, err := os.ReadFile(reportPath)
	if err != nil {
		t.Fatalf("expected report file to be readable: %v", err)
	}
	if string(got) != body {
		t.Errorf("report file contents = %q, want %q", string(got), body)
	}
	if !strings.Contains(string(got), "orders=42") {
		t.Errorf("report file did not preserve report details: %q", string(got))
	}
	if len(notifier.calls) != 1 {
		t.Fatalf("notifier calls = %d, want 1", len(notifier.calls))
	}
	if notifier.calls[0] != reportPath {
		t.Errorf("notifier path = %q, want %q", notifier.calls[0], reportPath)
	}
}

func TestWriteReportReturnsWriteErrorAndDoesNotNotify(t *testing.T) {
	dir := t.TempDir()
	blockingFile := filepath.Join(dir, "not-a-directory")
	if err := os.WriteFile(blockingFile, []byte("keep me"), 0o600); err != nil {
		t.Fatalf("failed to create blocking file: %v", err)
	}
	reportPath := filepath.Join(blockingFile, "daily-report.txt")
	notifier := &recordingNotifier{}

	err := WriteReport(reportPath, "body that cannot be written", notifier)
	if err == nil {
		t.Fatalf("WriteReport() error = nil, want write failure")
	}
	if len(notifier.calls) != 0 {
		t.Fatalf("notifier calls = %d, want 0 when write fails", len(notifier.calls))
	}
	if _, statErr := os.Stat(reportPath); statErr == nil {
		t.Errorf("unexpected report file exists at unwritable path %q", reportPath)
	}
	got, readErr := os.ReadFile(blockingFile)
	if readErr != nil {
		t.Fatalf("blocking file should still be readable: %v", readErr)
	}
	if string(got) != "keep me" {
		t.Errorf("blocking file contents = %q, want %q", string(got), "keep me")
	}
}

func TestWriteReportReturnsNotifierErrorAfterWritingReport(t *testing.T) {
	dir := t.TempDir()
	reportPath := filepath.Join(dir, "daily-report.txt")
	body := "Daily Report\norders=42\nstatus=green\n"
	notifyErr := errors.New("notifier unavailable")
	notifier := &recordingNotifier{err: notifyErr}

	err := WriteReport(reportPath, body, notifier)
	if !errors.Is(err, notifyErr) {
		t.Fatalf("WriteReport() error = %v, want notifier error %v", err, notifyErr)
	}
	if len(notifier.calls) != 1 {
		t.Fatalf("notifier calls = %d, want 1", len(notifier.calls))
	}
	if notifier.calls[0] != reportPath {
		t.Errorf("notifier path = %q, want %q", notifier.calls[0], reportPath)
	}

	got, readErr := os.ReadFile(reportPath)
	if readErr != nil {
		t.Fatalf("report should be written before notifier error is returned: %v", readErr)
	}
	if string(got) != body {
		t.Errorf("report file contents = %q, want %q", string(got), body)
	}
}
