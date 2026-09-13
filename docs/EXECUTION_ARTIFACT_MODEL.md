# Raw execution artifacts

Attempt outputs are staged by worker and sealed into SHA-256 CAS. Each descriptor records artifact type, blob hash, size, schema, trial and attempt; the artifact root is separate from the execution root. The execution API exposes raw artifact descriptors only and has no evidence publication, analysis or conclusion endpoint.
