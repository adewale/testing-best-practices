package reports

import (
    "errors"
    "path/filepath"
    "testing"
)

type fakeNotifier struct {
    err   error
    calls []string
}

func (f *fakeNotifier) Notify(path string) error {
    f.calls = append(f.calls, path)
    return f.err
}

func TestWriteReport(t *testing.T) {
    tests := []struct {
        name string
        dir  func(*testing.T) string
        note *fakeNotifier
        wantErr string
    }{
        {name: "success", dir: func(t *testing.T) string { return t.TempDir() }, note: &fakeNotifier{}},
        {name: "write failure", dir: func(t *testing.T) string { return filepath.Join(t.TempDir(), "missing", "child") }, note: &fakeNotifier{}, wantErr: "write"},
        {name: "notifier failure", dir: func(t *testing.T) string { return t.TempDir() }, note: &fakeNotifier{err: errors.New("notify failure")}, wantErr: "notify"},
    }
    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            err := WriteReport(tc.dir(t), "body", tc.note)
            if tc.wantErr == "" && err != nil { t.Fatalf("unexpected error: %v", err) }
            if tc.wantErr != "" && err == nil { t.Fatalf("expected %s error", tc.wantErr) }
        })
    }
}
