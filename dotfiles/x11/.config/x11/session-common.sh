# Shared X session configuration.
#
# Nothing reads this file directly: it is sourced from whichever entry point
# the platform happens to use, all of which are thin shims around this file.
#
#     ~/.xinitrc     startx / xinit
#     ~/.xprofile    display managers on Arch and most others
#     ~/.xsessionrc  Debian's /etc/X11/Xsession
#     ~/.profile     login shells, which some display managers also source
#
# Consequently everything here has to be idempotent: more than one of those
# can be read in a single session, and a desktop environment may well have
# done the same job already. The rule throughout is to look before setting,
# and to leave alone whatever is already configured.

# Guard against being sourced twice in one shell.
[ -n "${_X_SESSION_COMMON_SOURCED}" ] && return 0
_X_SESSION_COMMON_SOURCED=1

# None of this means anything without an X session, and ~/.profile is also
# read on tty and ssh logins, where setxkbmap earns nothing but a "Cannot
# open display" on stderr.
[ -n "${DISPLAY}" ] || return 0

### Keyboard ##########################################################

# Remap CapsLock to an actually useful key: compose. Desktop environments
# apply their own xkb options from their settings database after this runs
# -- Cinnamon does, via csd-keyboard -- so where the option is already set,
# leave it alone rather than fight over it.
if ! setxkbmap -query 2>/dev/null | grep -q 'compose:caps'; then
    setxkbmap -option compose:caps
fi

### Input method ######################################################

# Prefer ibus, fall back to uim. This can only probe what is *installed*:
# the session is only just starting, so there is nothing running to detect
# yet. If neither is installed, set ibus anyway, so that installing it later
# needs no config change.
if command -v ibus-daemon >/dev/null 2>&1; then
    im_module='ibus'
    im_daemon='ibus-daemon'
elif command -v uim-xim >/dev/null 2>&1; then
    im_module='uim'
    im_daemon='uim-xim'
else
    im_module='ibus'
    im_daemon=''
fi

export GTK_IM_MODULE="${im_module}" # Instructs the GTK immodule
export QT_IM_MODULE="${im_module}"  # Instructs the Qt immodule
export XMODIFIERS="@im=${im_module}"

# Starting the daemon is only our job when nothing else will do it, which is
# to say under startx -- hence X_SESSION_ROLE, which only ~/.xinitrc sets.
# Under a display manager the desktop environment starts its own and expects
# to own it: Cinnamon runs `ibus-daemon --panel disable --xim` so that it can
# supply its own panel, and a second daemon would only fight it.
if [ "${X_SESSION_ROLE}" = 'standalone' ] &&
   [ -n "${im_daemon}" ] &&
   ! pgrep -x "${im_daemon}" >/dev/null 2>&1; then
    case "${im_daemon}" in
        ibus-daemon)
            ibus-daemon -dx # -d: daemonize, -x: also serve XIM
            ;;
        uim-xim)
            uim-xim &
            ;;
    esac
fi

unset im_module im_daemon

### Machine-specific additions ########################################

# Source the "local" version. Still called .xinitrc.local, because that is
# the name the machines that have one already use.
if [ -e "${HOME}/.xinitrc.local" ]; then
    . "${HOME}/.xinitrc.local"
fi

# Optional config that can be toggled by the "local" version but implemented
# centrally. systemd's gcr-ssh-agent.socket exports this on its own on newer
# installs, so only step in if nothing has.
if [ "${USE_SSH_AGENT}" = 'gcr' ] && [ -z "${SSH_AUTH_SOCK}" ]; then
    export SSH_AUTH_SOCK="${XDG_RUNTIME_DIR}/gcr/ssh"
fi
