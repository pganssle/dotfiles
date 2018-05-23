#! /usr/bin/env bash

set -e
readonly PACKAGES=(
bash
git
vim
)

for pkg in "${PACKAGES[@]}"; do
    stow -d dotfiles -t ~ ${pkg}
done

stow -t ~ scripts
