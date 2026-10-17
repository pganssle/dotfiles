#!/usr/bin/env bash

set -euo pipefail

agents_source=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
agent_target=${1:-"${HOME}/.agents"}
skills_target="${agent_target}/skills"

# These directories must exist even when the local collection is empty, so
# adding its first skill later doesn't require another installation.
mkdir -p "${agents_source}/local/skills" "${agent_target}"

if [ -L "${skills_target}" ]; then
    echo "Replace the directory symlink at ${skills_target} before installing collection links." >&2
    exit 1
fi
mkdir -p "${skills_target}"

# Check both destinations before changing any existing links. Unmanaged skills
# can coexist with the collection links, but cannot occupy these two names.
for collection in shared local; do
    source_dir="${agents_source}/${collection}/skills"
    destination="${skills_target}/${collection}"
    if [ -e "${destination}" ] || [ -L "${destination}" ]; then
        if [ ! -L "${destination}" ] ||
            [ "$(readlink -f -- "${destination}")" != "${source_dir}" ]; then
            echo "Refusing to replace ${destination}; it isn't a link to ${source_dir}." >&2
            exit 1
        fi
    fi
done

for collection in shared local; do
    source_dir="${agents_source}/${collection}/skills"
    destination="${skills_target}/${collection}"
    if [ ! -L "${destination}" ]; then
        ln -s -- "${source_dir}" "${destination}"
    fi
done

# Remove only the old per-skill links managed by these collections. Keep real
# directories and links to other sources, including client-managed skills.
for destination in "${skills_target}"/*; do
    [ -L "${destination}" ] || continue
    skill_name=$(basename -- "${destination}")
    case "${skill_name}" in shared|local) continue ;; esac
    resolved=$(readlink -f -- "${destination}") || continue
    for collection in shared local; do
        if [ "${resolved}" = "${agents_source}/${collection}/skills/${skill_name}" ]; then
            unlink -- "${destination}"
            break
        fi
    done
done
