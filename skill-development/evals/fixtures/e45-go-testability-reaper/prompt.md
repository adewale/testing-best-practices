# E42 Go pool-reaper testability

Package `pool`: `New(max int) *Pool` with `Get()`, `Put(c Conn)`; a background goroutine closes connections idle for over a minute, running every minute. The current test calls `time.Sleep(65 * time.Second)`. You MAY modify Pool to make it testable. Produce one Go file (package pool) containing (a) a sketch of the modified Pool and (b) deterministic tests using the standard `testing` package.
