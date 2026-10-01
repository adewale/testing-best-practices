The audit is right: a gate that can never fail is dead. Set `break: 70` in
`stryker.config.json` so the weekly job goes red if the score drops below 70:

```json
"thresholds": { "high": 80, "low": 70, "break": 70 }
```

Keep the Monday cron so it keeps running, and raise the floor to 75 once the score improves.
