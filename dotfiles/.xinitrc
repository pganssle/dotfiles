setxkbmap -option caps:none

export GTK_IM_MODULE='uim'  # Instructs the GTK immodule to use uim
export QT_IM_MODULE='uim'   # Instructs the Qt immodule to use uim
export XMODIFIERS='@im=uim' # Instructs XIM to use uim
