# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
umask 0022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
	. "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Set NLTK data environment variable
export NLTK_DATA=.python_meta/nltk_data

# Shared X session config: compose key, input method, ssh agent. Some display
# managers source ~/.profile as part of starting the session (LightDM's
# Xsession does), so this is one of the entry points. It returns immediately
# when there is no X session, as on a tty or over ssh.
if [ -e "${HOME}/.config/x11/session-common.sh" ]; then
    . "${HOME}/.config/x11/session-common.sh"
fi

# Source the "local" version
if [ -e ${HOME}/.profile.local ]; then
    source ${HOME}/.profile.local
fi
