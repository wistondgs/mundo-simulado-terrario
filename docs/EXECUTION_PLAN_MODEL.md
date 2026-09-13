# Execution plan model

Planning re-verifies the exact preregistration and derives trials solely from its pinned TrialMatrix. The canonical plan includes trial identities, independent seeds, protocol, metrics, observer, failures, stopping and environment/software hashes. `plan_hash` excludes UI and execution identity; `execution_root_hash` binds it to execution and authorization.
