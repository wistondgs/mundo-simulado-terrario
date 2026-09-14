# Causal Fork Architecture

`POST_STATE(t*) / PRE_DECISION(t*+1)` is the only fork boundary. A sealed
`CausalForkSnapshot` restores two isolated real Terrario runtimes. Their shared
history is hashed before either branch is allowed to run. The control receives
an explicit C00 record; the intervention branch goes through the registry.

This core qualifies **A0_RANDOM × d0_differences only**. Other agents/worlds
fail closed; a same-seed rerun is never a fork.
