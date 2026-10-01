`.github/workflows/mutation.yml` runs Stryker on `src/core` every Monday. It has run 16 times.
`main` has not changed in that period, and every run reported 73.86% with
`thresholds.break: null`, so the job has never failed. A run takes about 10 minutes.
An audit flagged it as a dead gate because it cannot go red. The same job also runs our
12 defect-replay probes, which take about 2 minutes.

Give the lane some teeth. I was thinking of setting `break: 70`.
