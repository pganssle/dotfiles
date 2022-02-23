#! /usr/bin/bash
#
# Bash Aliases
#

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# Adding this allows us to use aliases with sudo, see: https://askubuntu.com/a/22043
alias sudo='sudo '

# colored GCC warnings and errors
export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Search hidden files with rg by default
alias rg='rg --hidden'

# Make an archived copy with rsync, showing progress and allowing resuming
alias rcopy='rsync -aAxuh --info=progress2'

# Make new SSH keys - use Curve 25519 with 100 rounds, no comment
alias ssh-newkey='ssh-keygen -t ed25519 -o -a 100 -C ""'

# Allow to set clipboard from command line
if xhost >& /dev/null; then
    alias setclip="xclip -selection c"
    alias getclip="xclip -selection c -o"
else
    # If no X display exists, create a file-based pseudo-clipboard
    _CLIPBOARD_DIR="/tmp/clipboard.Y8GUp42BMR"
    _get_clipboard_file() {
        clipboard_path="${_CLIPBOARD_DIR}/clipboard"
        if [[ ! -f "$clipboard_path" ]]; then
            mkdir -p "$_CLIPBOARD_DIR"
            touch "${clipboard_path}"
        fi
        echo "${clipboard_path}"
    }

    unalias setclip 2>/dev/null
    setclip() {
        cat > $(_get_clipboard_file)
    }

    unalias getclip 2>/dev/null
    getclip() {
        cat $(_get_clipboard_file)
    }
fi

# Copy the full path of a directory to the clipboard
copypath() {
    readlink -m ${1:-.} | head -c -1 | setclip
}

# Change directory to a newly created directory
mkcd() {
    if [[ $# -eq 0 ]]; then
        desired_dir=$(mktemp -d)
    elif [[ $# -ne 1 ]]; then
        echo "Pass only 0 or 1 argument to mkcd."
        return 2
    else
        desired_dir="$1"
        mkdir -p "$desired_dir"
    fi

    cd "$desired_dir"
}

# Copy a date (defaults to the current date) to the clipboard, in RFC-3339 format.
copydate() {
    if [[ $# -eq 0 ]]; then
        formatted_date=$(date --rfc-3339='seconds')
    elif [[ $# -eq 1 ]]; then
        formatted_date=$(date --rfc-3339='seconds' --date="$1")
    else
        echo "Too many arguments specified to copydate, use is copydate [date]"
        return 2
    fi

    echo "$formatted_date" | setclip
}

# Connect a SOCKS proxy
# TODO: Allow passing through the -D option
alias connect_socks="ssh -D 1080 -fnN"

# Install an optimized python with pyenv
python_opts="--enable-shared --enable-optimizations "
python_opts+="--with-computed-gotos --with-lto "
python_opts+="--enable-ipv6 --enable-loadable-sqlite-extensions "

# Source the "local" version
if [ -e ${HOME}/.bash_aliases.local ]; then
    source ${HOME}/.bash_aliases.local
fi

python_opts+="${LOCAL_PYTHON_COMPILE_OPTIONS} "
if ! alias pyenv-opt-install >/dev/null 2>&1; then
    alias pyenv-opt-install="env PYTHON_CONFIGURE_OPTS=\"${python_opts}\" pyenv install -v"
fi

if ! alias pyenv-opt-install-latest >/dev/null 2>&1; then
    alias pyenv-opt-install-latest="env PYTHON_CONFIGURE_OPTS=\"${python_opts}\" pyenv install-latest -v"
fi
