# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# Unlimited history file size
HISTSIZE=-1
HISTFILESIZE=-1

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# Set vim keybindings
set -o vi

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
    # We have color support; assume it's compliant with Ecma-48
    # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
    # a case would tend to support setf rather than setaf.)
    color_prompt=yes
    export TERM=xterm-256color
    else
    color_prompt=
    fi
fi

# Set up directory colors
if $(which dircolors) 2>&1 > /dev/null; then
    eval $(dircolors ~/.dircolors)
fi

#
# Set up the bash prompt - see http://stackoverflow.com/a/5687619
#

BLACK=$(tput setaf 0)
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
LIME_YELLOW=$(tput setaf 190)
YELLOW=$(tput setaf 3)
POWDER_BLUE=$(tput setaf 153)
BLUE=$(tput setaf 4)
MAGENTA=$(tput setaf 5)
CYAN=$(tput setaf 6)
WHITE=$(tput setaf 7)
BRIGHT=$(tput bold)
NORMAL=$(tput sgr0)
BLINK=$(tput blink)
REVERSE=$(tput smso)
UNDERLINE=$(tput smul)
reset="$(tput sgr0)"
export GITCOLOR="${RED}"

# Find the first matching location for git-prompt and git-completion
# and source it
GIT_PROMPT_LOCS=("$HOME/local/libexec/git-prompt.sh" "/usr/share/git/completion/git-prompt.sh" "/usr/share/git/git-prompt.sh" "/etc/bash_completion.d/git-prompt")
GIT_COMPLETION_LOCS=("$HOME/local/libexec/git-completion.bash" "/usr/share/git/completion/git-completion.bash")

git_prompt_found=false
for GIT_PROMPT_LOC in ${GIT_PROMPT_LOCS[@]}; do
    if [[ -f "$GIT_PROMPT_LOC" ]]; then
        source "$GIT_PROMPT_LOC"
        git_prompt_found=true
        break
    fi
done

for GIT_COMPLETION_LOC in ${GIT_COMPLETION_LOCS[@]}; do
    if [[ -f "$GIT_COMPLETION_LOC" ]]; then
        source "$GIT_COMPLETION_LOC"
        break
    fi
done

export PS1COLOR="${GREEN}"
export MAXPS1CHARS=20
export MYPS='$(echo -n "${PWD/#$HOME/~}" | awk -F "/" '"'"'{
if (length($0) > 20) { if (NF>4) print $1 "/" $2 "/.../" $(NF-1) "/" $NF;
else if (NF>3) print $1 "/" $2 "/.../" $NF;
else print $1 "/.../" $NF; }
else print $0;}'"'"')'

if [ "$git_prompt_found" = true ]; then 
    PS1='[$(__git_ps1 "\[${GITCOLOR}\]%s\[${reset}\]@")\[${PS1COLOR}\]$(eval "echo -en ${MYPS}")\[${reset}\]]$ '
else
    echo "Warning: Git prompt not found"
    PS1='[\[${PS1COLOR}\]$(eval "echo -en ${MYPS}")\[${reset}\]]$ '
fi

unset git_prompt_found
unset color_prompt force_color_prompt

# Enable customization of window title in local files
export BASE_PS1=${PS1}

function expand_ps1() {
    # This adds custom expansions under the \C{} command

    # - \C{venv} -> Current virtual environment
    # If VIRTUAL_ENV exists, it should be rendered as '(<venv>) '
    venv_info='${VIRTUAL_ENV:+(}${VIRTUAL_ENV##*/}${VIRTUAL_ENV:+) }'
    out=${1/\\C\{venv\}/${venv_info}}

    echo $out
}


function set_title() {
    # This adds some custom expansions under the \C{} command

    # If this is an xterm set the title to dir
    case "$TERM" in
    xterm*|rxvt*)
        PS1='\[\e]0;'$(expand_ps1 ${1})'\a\]'${BASE_PS1}
        ;;
    *)
        ;;
    esac
}

# Set the default window title
PS1_TITLE='\C{venv}\w'
set_title $PS1_TITLE

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Activate virtualenvwrapper
function has_virtualenvwrapper() {
    if command -v virtualenv 1>/dev/null 2>&1 && \
       command -v virtualenvwrapper.sh 1>/dev/null 2>&1; then
        echo true
    else
        echo false
    fi
}

# Set up pyenv - first add it to the PATH and see if it worked
export PYENV_ROOT="$HOME/.pyenv"
OLD_PATH=$PATH
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(pyenv init -)"

    # Check if pyenv virtualenvwrapper is installed
    if [ $(has_virtualenvwrapper) = true ] && \
       pyenv commands | grep -x virtualenvwrapper 1>/dev/null 2>&1; then
        pyenv virtualenvwrapper_lazy
    fi
else
    export PATH=$OLD_PATH
    unset OLD_PATH
    unset PYENV_ROOT
    if [ $(has_virtualenvwrapper) = true ]; then
        source virtualenvwrapper_lazy.sh
    fi
fi

# Set up ruby gems
if command -v ruby 1>/dev/null 2>&1; then
    export PATH="$PATH:$(ruby -e 'print Gem.user_dir')/bin"
fi

# Add bash scripts to the path
if [ -d "$HOME/.bash_scripts" ]; then
    export PATH="$PATH:$HOME/.bash_scripts"
fi


# Add local scripts to the path
if [ -d "$HOME/local/bin" ]; then
    export PATH="$PATH:$HOME/local/bin"
fi

if [ -d "$HOME/.local/bin" ]; then
    export PATH="$PATH:$HOME/.local/bin"
fi

# Add cargo scripts ot the path
if [ -d "$HOME/.cargo/bin" ]; then
    export PATH="$PATH:$HOME/.cargo/bin"
fi


# Source the "local" version
if [ -e ${HOME}/.bashrc.local ]; then
    source ${HOME}/.bashrc.local
fi
