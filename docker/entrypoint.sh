#!/usr/bin/env bash
# Prepare the container's view of a bind-mounted repository, then exec.
#
# Everything here exists to keep the container from lying about the host, or
# writing where the host would notice.
set -euo pipefail

REPO="${TERRARIO_REPO:-/home/wis/mundo simulado terrario}"
cd "$REPO"

# `git status` refuses a repository owned by another uid and returns non-zero.
# Terrario's software-manifest helpers swallow that failure and record an empty
# git_commit with dirty_tree=False, which is a preregistration asserting a clean
# tree it never checked. Declaring the directory safe keeps git honest.
git config --global --add safe.directory "$REPO" 2>/dev/null || true

# playwright.config.js runs `.venv/bin/python`. The host's .venv is 7.6 GB, has
# absolute host paths baked into pyvenv.cfg and an absolute symlink to
# /usr/bin/python3, so it cannot be reused. The image builds its own venv at
# that exact path and Docker populates the shadowing volume from it.
#
# If the venv is missing, the volume was pre-created empty (Docker only seeds a
# volume it creates itself). Say so and stop, rather than run the host's
# interpreter or a half-built environment by accident.
if [ ! -x "$REPO/.venv/bin/python" ]; then
    echo "terrario: no hay intérprete en $REPO/.venv/bin/python." >&2
    echo "terrario: el volumen terrario-venv existe pero está vacío. Recrealo con:" >&2
    echo "terrario:   docker compose -f docker/compose.yaml down -v" >&2
    exit 1
fi

# node_modules is likewise shadowed by a volume. package-lock.json is gitignored
# but present through the bind mount, and execution/service.py hashes it into
# package_lock_hash, so it must not be regenerated with different contents.
if [ ! -d "$REPO/node_modules/@playwright/test" ]; then
    echo "terrario: instalando node_modules del contenedor (npm ci)" >&2
    npm ci --no-audit --no-fund
fi

exec "$@"
