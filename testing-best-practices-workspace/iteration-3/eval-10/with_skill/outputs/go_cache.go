// Package cache provides a simple in-memory key-value cache with TTL support.
package cache

import (
	"sync"
	"time"
)

// Cache is a thread-safe in-memory key-value store with TTL.
type Cache struct {
	mu    sync.RWMutex
	items map[string]item
}

type item struct {
	value     interface{}
	expiresAt time.Time
}

// New creates a new Cache.
func New() *Cache {
	return &Cache{items: make(map[string]item)}
}

// Set stores a value with the given TTL. If ttl is 0, the item never expires.
func (c *Cache) Set(key string, value interface{}, ttl time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()

	var expiresAt time.Time
	if ttl > 0 {
		expiresAt = time.Now().Add(ttl)
	}

	c.items[key] = item{value: value, expiresAt: expiresAt}
}

// Get retrieves a value by key. Returns the value and true if found and not
// expired, or nil and false otherwise.
func (c *Cache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	it, ok := c.items[key]
	if !ok {
		return nil, false
	}

	if !it.expiresAt.IsZero() && time.Now().After(it.expiresAt) {
		return nil, false
	}

	return it.value, true
}

// Delete removes a key from the cache.
func (c *Cache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.items, key)
}

// Len returns the number of items in the cache (including expired).
func (c *Cache) Len() int {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return len(c.items)
}

// Clear removes all items from the cache.
func (c *Cache) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.items = make(map[string]item)
}
