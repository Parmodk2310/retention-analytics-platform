# Runbook: Experiment sample-ratio mismatch

## Trigger

Treat SRM as active when the configured test reports `p < 0.01`. Stop interpreting treatment
effects until the allocation discrepancy is explained.

## Immediate actions

1. Mark the decision as invalid or paused; do not ship based on lift or significance.
2. Record experiment ID, expected allocation, observed counts, eligibility window and SRM method.
3. Preserve assignment, exposure and outcome data for investigation.

## Investigation

- Confirm allocation configuration did not change mid-experiment.
- Recompute deterministic assignment for a sample of user IDs.
- Check uniqueness of experiment/user assignments.
- Compare assignment counts with actual exposure counts.
- Verify eligibility and exclusion rules are identical across variants.
- Segment SRM by platform, app version, geography, channel and day.
- Check logging loss, retries, bots and duplicate exposure events.
- Confirm experiment lifecycle timestamps and outcome windows.

## Resolution

Correct instrumentation or allocation before resuming. If affected observations cannot be
reconstructed reliably, restart with a new experiment identifier. Do not remove inconvenient rows
or repeatedly change the SRM threshold.

## Close criteria

- root cause documented;
- affected data range identified;
- regression test or monitor added;
- allocation remains healthy for an agreed observation window;
- treatment-effect analysis is recomputed from trustworthy exposure data.

SRM indicates a randomization or data-quality problem; it does not explain which variant is better.
