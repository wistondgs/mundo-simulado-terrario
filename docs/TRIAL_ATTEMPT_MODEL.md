# Trial and attempt model

A plan materializes pinned trial intents and reserved execution jobs. Attempts are distinct ordinal records, so a retry is never a hidden overwrite. Pause is supported at attempt boundaries. Only `RESTORABLE_EXACT` checkpoints may resume an attempt; observational checkpoints are raw forensics only.
