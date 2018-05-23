#! /usr/bin/env bash

set -e
readonly PACKAGES=(
bash
git
vim
)

# Create ~/.vim so it doesn't end up as a symlink
if [ ! -d "~/.vim" ]; then
    mkdir ~/.vim
fi

for pkg in "${PACKAGES[@]}"; do
    stow -d dotfiles -t ~ ${pkg}
done

stow -t ~ scripts
