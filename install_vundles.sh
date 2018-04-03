#!/usr/bin/env bash
set -e

VUNDLE_DIR=${HOME}/.vim/bundle/Vundle.vim

# Install vundle if it doesn't exist
if [ ! -d "${VUNDLE_DIR}" ]; then
    git clone https://github.com/VundleVim/Vundle.vim.git ${VUNDLE_DIR}
fi

# Install all the vundle plugins
vim +PluginInstall +qall
