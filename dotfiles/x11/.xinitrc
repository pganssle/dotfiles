# Entry point for startx / xinit.
#
# There is no session manager here, so this session has to configure itself
# rather than defer to a desktop environment -- see X_SESSION_ROLE in
# session-common.sh, which gates starting the input method daemon.
X_SESSION_ROLE='standalone'
. "${HOME}/.config/x11/session-common.sh"
