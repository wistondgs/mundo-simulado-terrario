# syntax=docker/dockerfile:1
#
# Terrario development and test harness.
#
# THIS IS NOT AN EXECUTION ENVIRONMENT FOR SCIENCE. A preregistration seals
# observed_environment (operating system, python, torch, cuda) into its bundle
# root hash, and nothing in the execution path compares a preregistered
# environment against the one that actually runs. A container therefore produces
# records that are not comparable with the host's without re-baselining
# ENVIRONMENT.md. Scientific execution stays on the host.
#
# What this image is for: running the test suites and the lab UI in a disposable
# environment, so ports, stray servers and runtime state cannot collide with the
# host's.
#
# The image carries ONLY the toolchain. The repository arrives as a bind mount at
# runtime, at its host absolute path, because an absolute scenario path is hashed
# into config_hash and sealed into trial artifacts.

ARG PLAYWRIGHT_VERSION=v1.63.0
FROM mcr.microsoft.com/playwright:${PLAYWRIGHT_VERSION}-noble

# Ubuntu 24.04 ships Python 3.12.3, which is the interpreter ENVIRONMENT.md
# records. git is mandatory, not optional: preregistration and execution derive
# git_commit and dirty_tree from `git rev-parse` / `git status --porcelain`, and
# both helpers swallow failure and return an empty string. A container without
# git would silently record a blank commit and dirty_tree=False -- a
# preregistration that claims a clean tree it never verified.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.12 python3.12-venv python3-pip git \
 && rm -rf /var/lib/apt/lists/*

# The GPU on this host is dead at the driver level (Code 43 / "Failed to copy
# vbios to system memory", ENVIRONMENT.md), so the harness carries the CPU wheel
# and no CUDA libraries. That is a deliberate trade, not a free one.
#
# torch's CPU kernels are NOT bit-identical across build variants. Measured on
# this repo: with 2.5.1+cpu, A4_ADVANCED prediction_errors[1] reads 0.0878492892
# where the fixture recorded by the host's 2.5.1+cu121 has 0.0878492594. That
# single ~1e-8 difference changes semantic_digest and fails
# test_d2_d3_d4_a0_a1_a4_match_checked_in_behavior, which is therefore excluded
# from the container run and stays a host-only gate. See docs/DOCKER_HARNESS.md.
#
# Set TORCH_INDEX_URL to the cu121 index to reproduce the host build byte for
# byte at the cost of roughly 3 GB of CUDA libraries for a GPU that cannot run.
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
ARG TORCH_VERSION=2.5.1
ARG NUMPY_VERSION=2.5.2

# playwright.config.js hardcodes `.venv/bin/python` as its webServer command, so
# the container needs a venv at exactly that path and the config must not be
# edited for the container's convenience.
#
# The venv is built at its FINAL path inside the image. Docker initialises a new
# named volume from the image content at the path it shadows, so the .venv
# volume comes up already populated and correctly owned -- no multi-gigabyte
# copy on first run. The entrypoint keeps a seeding fallback for the case where
# a volume is reused or pre-created empty.
ARG REPO_PATH="/home/wis/mundo simulado terrario"
ENV VENV_SRC="${REPO_PATH}/.venv"
# The venv is created AS uid 1000 rather than chowned afterwards: a chown -R in
# a later layer rewrites every file's metadata and duplicates the entire 1.16 GB
# venv layer (measured with `docker history`). Owning it from the start costs
# nothing. The base image already has uid 1000 as `ubuntu`.
RUN mkdir -p "$VENV_SRC" && chown 1000:1000 "$VENV_SRC" "${REPO_PATH}"
USER 1000
RUN python3.12 -m venv "$VENV_SRC" \
 && "$VENV_SRC/bin/pip" install --no-cache-dir --upgrade pip \
 && "$VENV_SRC/bin/pip" install --no-cache-dir \
        --index-url "${TORCH_INDEX_URL}" "torch==${TORCH_VERSION}" \
 && "$VENV_SRC/bin/pip" install --no-cache-dir \
        "numpy==${NUMPY_VERSION}" "PyYAML>=6.0" "pytest>=8" \
        "safetensors>=0.4" "pyarrow>=15" "zarr>=2.17"

# A named volume inherits the ownership of the image directory it shadows, so
# these must exist and be owned by 1000 before any volume is created from them.
# Otherwise they come up root-owned and the uid-1000 container cannot write into
# its own node_modules, data root or HOME.
USER root
RUN mkdir -p "${REPO_PATH}/node_modules" "${REPO_PATH}/.terrario" /tmp/terrario-home \
 && chown 1000:1000 "${REPO_PATH}/node_modules" "${REPO_PATH}/.terrario" /tmp/terrario-home

# pyarrow is not optional here despite being an extra: without it the trace
# writer degrades to JSONL and the behaviour fixture, which records
# events/consequence.parquet, no longer matches.

# A named volume inherits the ownership of the image directory it shadows. These
# paths do not otherwise exist in the image, so Docker would create them
# root-owned and the uid-1000 container could not write into its own .venv,
# node_modules, data root or HOME. Creating them owned by 1000 up front is what
# makes `user: "1000:1000"` workable.
COPY entrypoint.sh /usr/local/bin/terrario-entrypoint
RUN chmod +x /usr/local/bin/terrario-entrypoint

ENTRYPOINT ["/usr/local/bin/terrario-entrypoint"]
CMD ["bash"]
