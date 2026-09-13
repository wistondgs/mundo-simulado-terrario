# Scientific playback contract

Playback reads only a matching `SCIENTIFIC_TRACE` descriptor from CAS and rejects unknown attempts, malformed JSON and mismatched attempt identities. Pages are bounded to 256 frames and carry a backend cursor. It is explicitly `PLAYBACK`, not live state.
