#! /usr/bin/env bash

set -e
readonly PACKAGES=(
bash
git
vim
emacs
tmux
x11
)

# Create ~/.vim so it doesn't end up as a symlink
if [ ! -d "${HOME}/.vim" ]; then
    mkdir ~/.vim
fi

for pkg in "${PACKAGES[@]}"; do
    stow --adopt -d dotfiles -t ~ ${pkg}
done

stow -d dotfiles -t ~/.ipython/profile_default ipython_profile_default

stow -t ~ scripts
stow -t ~ config_files

# Codex scans collections recursively, so new skills need no Stow refresh.
bash agents/install-skills.sh "${HOME}/.agents"

# Claude Code scans immediate skill directories, so keep its flat Stow layout.
readonly AGENT_HOMES=(
    "${HOME}/.claude"
)

for agent_home in "${AGENT_HOMES[@]}"; do
    for pkg in shared local; do
        [ -d "agents/${pkg}" ] || continue

        # Create the category directories (skills, agents, ...) up front so
        # that stow links the individual skills instead of folding the whole
        # category into a single symlink; the shared and local packages have
        # to be able to share a directory.
        for category in "agents/${pkg}"/*/; do
            [ -d "${category}" ] || continue
            mkdir -p "${agent_home}/$(basename "${category}")"
        done

        stow -d agents -t "${agent_home}" "${pkg}"
    done
done
