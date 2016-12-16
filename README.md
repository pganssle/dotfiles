This repository contains the dotfiles I use on my standard Linux install, using Bash, plus a small python script which "installs" them in the home directory, either as a symbolic link (default) or by copying the files.

Usage:
```
usage: install_dotfiles.py [-h] [-d DIRECTORY] [-c] [-hd HOME]
                           [-bl BACKUP_LOC] [-r] [-e EXCLUDE] [-i INCLUDE]
                           [-a ADDITIONAL]

Install dotfiles as symbolic links to this directory.

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory where the dotfiles are stored.
  -c, --copy            Use the -c flag if you want to copy these files to the
                        home directory instead of using symbolic links.
  -hd HOME, --home HOME
                        Use to specify where the home directory is (default is
                        ~)
  -bl BACKUP_LOC, --backup-loc BACKUP_LOC
                        Location to back up old files that are not already
                        symbolic links to these dotfiles.
  -r, --restore         Restores dotfiles from the backup location when the
                        dotfile exists both as a symbolic link and in the
                        backup location.
  -e EXCLUDE, --exclude EXCLUDE
                        Semicolon-delimited list of dotfiles to ignore.
  -i INCLUDE, --include INCLUDE
                        Semicolon-delimited list of dotfiles to include. If
                        unspecified, all files starting with . will be
                        included.
  -a ADDITIONAL, --additional ADDITIONAL
                        If specified, this should point to a file containing a
                        newline-delimited list of files to install above and
                        beyond the -i argument. These should be absolute or
                        relative to the current directory, and all must exist.
```

By default, your existing dotfiles will be backed up in the 'backup' file.