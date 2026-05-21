package reportfixture

import "os"

type Notifier interface { Notify(string) error }

func WriteReport(path string, body string, notifier Notifier) error {
	if err := os.WriteFile(path, []byte(body), 0o600); err != nil { return err }
	return notifier.Notify(path)
}
