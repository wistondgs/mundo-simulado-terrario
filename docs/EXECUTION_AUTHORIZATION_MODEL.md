# Execution authorization

Authorization is immutable, root-scoped and actor-attributed. `ONE_EXECUTION`, `N_EXECUTIONS`, `REPLICATION_SERIES`, and `UNTIL_EXPIRY` require a positive explicit quota; replication additionally needs a group and expiry needs an expiry timestamp. CPU/GPU, memory, disk, process and wall-clock limits are mandatory. Consumption is atomic at first start and never refunded.
