#! /usr/bin/env python3
DESCRIPTION = \
"""Install dotfiles as symbolic links to this directory."""

import os
import shutil

def get_dotfiles(file_dir):
    """ Get all the dotfiles in a given directory (not recursive) """
    return [os.path.join(file_dir, x)
            for x in os.listdir(file_dir)
            if x.startswith('.')]


def check_for_conflicts(file_list):
    """ Verify that a given file list has no conflicting names """
    file_list = list(file_list)
    file_names = [os.path.split(os.path.abspath(x))[1] for x in file_list]

    if len(file_names) != len(set(file_names)):
        duplicates = {}
        for file_name, file_loc in zip(file_names, file_list):
            duplicates.setdefault(file_name, []).append(file_loc)

        duplicates = {k: v for k, v in duplicates.items()
                      if len(v) > 1}

        msg = 'Duplicate file names found:\n'
        for k, v in duplicates.items():
            msg += '  {}: {}\n'.format(k, ','.join(v))

        raise ValueError(msg)


def read_file_list(fpath, must_exist=True):
    """ Read a list of files from a newline-delimited file. """
    file_list = []
    with open(fpath, 'r') as f:
        for line in f:
            fpath = line.strip()
            file_list.append(fpath)

    if must_exist:
        missing_files = []
        for fpath in file_list:
            if not os.path.exists(fpath):
                missing_files.append(fpath)

        if len(missing_files):
            raise ValueError('Files missing: {}'.format(','.join(missing_files)))

    return file_list


def resolve_link(fpath, visited=None):
    """
    If fpath is a link, this follows all symbolic links until
    reaches a path that is not a link, then returns the absolute path to that.
    """
    abs_fpath = os.path.abspath(fpath)

    if not os.path.islink(fpath):
        return abs_fpath
    else:
        visited = visited or set()

        abs_linkpath = os.path.abspath(os.readlink(abs_fpath))
        if abs_linkpath in visited:
            raise ValueError('Loop detected in symbolic link!')
        else:
            visited.add(abs_linkpath)

        return resolve_link(abs_linkpath, visited=visited)


def get_move_list(dest_dir, file_list, ignore_symlinks=True):
    """ Get a mapping between the file list and their destinations """
    file_list = [os.path.abspath(x) for x in file_list]
    dest_file_list = [os.path.split(x)[1] for x in file_list]
    new_locations = [os.path.abspath(os.path.join(dest_dir, x))
                     for x in dest_file_list]

    # Create a mapping between the original file list and new locations,
    # ignoring things that are already symbolic links to one another
    move_list = {}
    for src, dst in zip(file_list, new_locations):
        if ignore_symlinks:
            src_full_path = resolve_link(src)
            dst_full_path = resolve_link(dst)

            if src_full_path == dst_full_path:
                continue

        move_list[src] = dst

    return move_list


def copy_files(move_list, symlink=True, ignore_missing=False):
    for src, dst in move_list.items():
        if not os.path.exists(src):
            if ignore_missing:
                continue
            else:
                raise ValueError('Missing base file {}'.format(src))

        if os.path.exists(dst):
            os.remove(dst)
            pass

        if symlink:
            os.symlink(src, dst)
        else:
            shutil.copy2(src, dst)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-d', '--directory', type=str, default='dotfiles',
        help='Directory where the dotfiles are stored.')

    parser.add_argument('-c', '--copy', action='store_true',
        help='Use the -c flag if you want to copy these files to the home '
             'directory instead of using symbolic links.')

    parser.add_argument('-hd', '--home', type=str, default=None,
        help='Use to specify where the home directory is (default is ~)')

    parser.add_argument('-bl', '--backup-loc', type=str, default='backup',
        help='Location to back up old files that are not already symbolic '
             'links to these dotfiles.')

    parser.add_argument('-r', '--restore', action='store_true',
        help='Restores dotfiles from the backup location when the dotfile '
             ' exists both as a symbolic link and in the backup location.')

    parser.add_argument('-e', '--exclude', type=str, default=None,
        help='Semicolon-delimited list of dotfiles to ignore.')

    parser.add_argument('-i', '--include', type=str, default=None,
        help='Semicolon-delimited list of dotfiles to include.\n'
             'If unspecified, all files starting with . will be included.')

    parser.add_argument('-a', '--additional', type=str, default=None,
        help='If specified, this should point to a file containing a '
             'newline-delimited list of files to install above and beyond '
             'the -i argument. These should be absolute or relative to the '
             'current directory, and all must exist.')

    args = parser.parse_args()

    restore = args.restore
    backup_dir = args.backup_loc
    if restore:
        base_dir = args.backup_loc
    else:
        base_dir = args.directory

    if not os.path.exists(base_dir):
        raise ValueError('Base directory {} does not exist!'.format(base_dir))

    dest_dir = args.home or os.path.expanduser('~')
    if not os.path.exists(dest_dir):
        raise ValueError('Home directory {} does not exist!'.format(home_dir))

    # Get the file list now
    if args.include is None:
        include_files = get_dotfiles(base_dir)
    else:
        include_files = args.include.split(';')

    # Add any additional files
    if args.additional is not None:
        additional_files = read_file_list(args.additional, must_exist=False)

        include_files += additional_files

    include_files = set(include_files)   # These need to be unique anyway.

    # Remove any excluded files
    if args.exclude is not None:
        excluded_files = set(args.exclude.split(';'))

        include_files -= excluded_files

    include_files = list(include_files)

    # Check for conflicting file names to avoid things like:
    # dotfiles/1/.bashrc -> ~/.bashrc
    # dotfiles/2/.bashrc -> ~/.bashrc
    check_for_conflicts(include_files)

    if not restore:
        # Time to do a backup
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        backup_list = get_move_list(backup_dir, include_files, ignore_symlinks=True)
        copy_files(backup_list, symlink=False)

    if not args.copy:
        move_list = get_move_list(dest_dir, include_files, ignore_symlinks=True)
    else:
        move_list = get_move_list(dest_dir, include_files, ignore_symlinks=False)

    copy_files(move_list, symlink=not args.copy)

