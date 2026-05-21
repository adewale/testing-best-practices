package reports

import (
    "net/http"
    "testing"
)

func TestWriteReport(t *testing.T) {
    _ = http.DefaultClient
    err := WriteReport("/tmp/report.txt", "body", realNotifier{})
    if err != nil { t.Fatal(err) }
}
