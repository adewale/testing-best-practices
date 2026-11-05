The save/load identity is the persistence contract, so compare the full
canonical store. A narrow quota assertion can be an additional focused test,
but it must not replace the whole-state roundtrip check.

```json
{
  "retain_whole_state": true,
  "quota_only_replacement": false,
  "contract": "save_load_identity"
}
```
