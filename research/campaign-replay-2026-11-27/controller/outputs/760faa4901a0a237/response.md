## Findings

1. **The registration test could pass while a renewed browser missed reminders.** It posted identical keys twice and counted endpoints. I extended the two-device test to post fresh laptop keys at the same endpoint between reminders. It checks for one request to that endpoint and decrypts its body as “Bins out” with the new keys. The RFC 8291 vector, first reminder’s per-device decryption and phone’s 410 cleanup still run. See `test/web-push.test.ts` lines 93, 202, 241 and 250.
2. **Transient push failures lack a retention check.** The supplied test exercises 410 and successful delivery. A 404 removal case and a successful send after a 503 would catch a change that drops a live device or keeps an expired one. See `pda-spec.md:772`, `src/agent.ts:520` and `test/web-push.test.ts:253`.
3. **The device-limit test follows the production constant.** It proves oldest-first eviction. Registering eleven devices and expecting the ten newest would also protect the documented limit. See `pda-spec.md:234` and `test/web-push.test.ts:218`.

## Scope and verification

PDA specifies that registration keeps both browser keys, that a browser posts its replacement subscription, and that notifications use that browser’s keys (`pda-spec.md` lines 149, 772–773). I traced Settings and renewal through `src/ui/notifications.tsx:69`, `public/sw.js:35`, `src/index.ts:383`, `src/agent.ts:535` and `src/web-push.ts:285`. The reminder originates at `src/schedules.ts:200`. The helper invokes the Worker at `test/agent-helpers.ts:71`, and the fake service captures ciphertext at `test/worker.ts:1287`. I also reviewed the supplied crash, approval-recovery, task-request, interop approval-delivery and UI history tests during selection.

I ran these commands from `work/repo/` with Node 24.22.3.

```sh
node node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/vitest.config.ts test/web-push.test.ts
node node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/ui/vitest.config.ts test/ui/workspace.test.tsx -t "notification settings"
npm run typecheck
git diff --check
git diff --exit-code -- src/web-push.ts
```

The Workers file passed 9/9 at baseline. I temporarily changed the SQL update to keep the old `auth` while storing the new `p256dh`. The original tests still passed 9/9. With the revised test, eight passed and only renewal failed at receiver decryption on line 260. Restoring production code gave 9/9 in 12.74 seconds, including 0.904 seconds in tests. The page selection passed 4/4 with 49 filtered out. Typechecking and both Git checks passed. The final patch changes one test file, +8/−3 lines.

The snapshot supplies 56 of the inventory’s 155 named modules. The three successful hosted job records describe the original pin `c0a9a85`. Local evidence covers Worker registration through ciphertext capture and simulated receipt. Browser renewal-event dispatch and on-device display require separate evidence.
