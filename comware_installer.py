#!/usr/bin/python
# Refactor by Rohmat Tri Indra

# This is refactor script from https://github.com/aruba/aruba-ansible-modules/blob/master/aruba_module_installer/aruba_module_installer.py

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from subprocess import check_output
from shutil import copytree, copyfile, rmtree
from os.path import dirname, realpath, exists, isdir
from os import remove
from sys import exit
from re import search
import errno


COLORRED = "\033[0;31m{0}\033[00m"


SW_PATHS = {'module': 'modules/network/comware'}

CMD = 'ansible --version'

SRC_PATH = dirname(realpath(__file__))+'/library/'

ANS_PATH = ''

def define_arguments():

    description = ('This tool installs all files/directories required by '
                   'Comware7,'
                   '\n\n'
                   'Requirements:'
                   '\n\t- Linux OS only'
                   '\n\t- Ansible release version 2.5 or later installed'
                   '\n\t- Python 2.7 or 3.5+ installed'
                   )

    epilog = ('Directories added:'
              '\n\t- <ansible_module_path>/modules/network/comware'
             )

    parser = ArgumentParser(description=description,
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog=epilog)
    parser.add_argument('-r', '--remove', required=False,
                        help=('remove all files & directories installed '
                              'by this script.'),
                        action='store_true')
    parser.add_argument('--reinstall', required=False,
                        help=('remove all files & directories installed '
                              'by this script. Then re-install.'),
                        action='store_true')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--switch', required=False,
                       help=('only install files/directories required for '
                             'Comware.'
                             ),
                       action='store_true')
    return parser.parse_args()


def find_module_path():

    global CMD, COLORRED

    output = check_output(CMD, shell=True).strip()

    re_path = search(r"ansible python module location = (?P<path>\S+)",
                     output.decode('utf-8'))

    re_version = search(r"ansible\s(?P<version>\d\S+\d)", output.decode('utf-8'))

    if re_path and re_version:

        re_version = re_version.groupdict()['version']
        re_path = re_path.groupdict()['path']

        # Validate Ansible version is supported
        if '2.5' <= re_version <= '2.9.9':
            return re_path+'/'
        else:
            exit(COLORRED.format('There was an issue with your '
                                 'ansible version: {}\n'
                                 'The Aruba Modules support Ansible release '
                                 'versions 2.5 or later.').format(re_version))
    else:
        exit(COLORRED.format('There was an issue finding your '
                             'ansible version.\n'
                             'Please run \'ansible --version\' from bash'
                             ', resolve any errors, and verify version'
                             ' is release version 2.5 or later.'))


def install_sw_modules():

    global SW_PATHS, SRC_PATH, COLORRED, ANS_PATH

    # Copy each directory and file to ansible module location
    for source, path in SW_PATHS.items():
        # If directories or files exist already, do nothing
        if exists(ANS_PATH+path):
            print(COLORRED.format('{} already exists'
                                  ' at {}...\n'.format(path, ANS_PATH+path)))
        else:
            print('Copying {} to {}...\n'.format(path, ANS_PATH+path))
            if isdir(SRC_PATH+path):
                copytree(SRC_PATH+path, ANS_PATH+path)
            else:
                copyfile(SRC_PATH+path, ANS_PATH+path)


if __name__ == "__main__":

    args = define_arguments()

    try:

        ANS_PATH = find_module_path()

        if args.remove:
            remove_modules()
        elif args.reinstall:
            remove_modules()
            install_sw_modules()
            install_wlan_modules()
        elif args.switch:
            install_sw_modules()
        else:
            install_sw_modules()

    except (OSError, IOError) as e:
        if (e[0] == errno.EACCES):
            print(e)
            if args.remove:
                exit(COLORRED.format("You need root permissions to execute "
                                     "this script against "
                                     "these files/directories.\n\n"
                                     "re-run the installer using\n"
                                     "sudo python"
                                     "comware install module -r"))
            else:
                exit(COLORRED.format("You need root permissions to execute "
                                     "this script against "
                                     "these files/directories.\n\n"
                                     "re-run the installer using\n"
                                     "sudo python "
                                     "comware installer.py"))
        else:
            raise e
