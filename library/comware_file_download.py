#!/usr/bin/python

DOCUMENTATION = """
---

module: comware_file_download
short_description: Download a file from remote Comware v7 device
description:
    - Download a file from remote Comware v7 device
version_added: 1.8
category: System (RW)
options:
    file:
        description:
            - File (including absolute path of remote file) that will be
              downloaded from device
        required: true
        default: null
        choices: []
        aliases: []
    local_path:
        description:
            - Destination file on local filesystem (full path)
        required: false
        default: <file>
        choices: []
        aliases: []
    hostname:
        description:
            - IP Address or hostname of the Comware v7 device that has
              NETCONF enabled
        required: true
        default: null
        choices: []
        aliases: []
    username:
        description:
            - Username used to login to the switch
        required: true
        default: null
        choices: []
        aliases: []
    password:
        description:
            - Password used to login to the switch
        required: true
        default: null
        choices: []
        aliases: []
    port:
        description:
            - NETCONF port number
        required: false
        default: 830
        choices: []
        aliases: []

"""

EXAMPLES = """

# copy file
- comware_file_download: file=flash:/file local_path=flash:/otherfile username={{ username }} password={{ password }} hostname={{ inventory_hostname }}

"""
import socket

try:
    HAS_PYHP = True
    from pyhpecw7.comware import HPCOM7
    from pyhpecw7.features.file_download import FileDownload
    from pyhpecw7.errors import *
except ImportError as ie:
    HAS_PYHP = False


def safe_fail(module, device=None, **kwargs):
    if device:
        device.close()
    module.fail_json(**kwargs)


def safe_exit(module, device=None, **kwargs):
    if device:
        device.close()
    module.exit_json(**kwargs)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            file=dict(required=True),
            local_path=dict(),
            hostname=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            port=dict(type='int', default=830)
        ),
        supports_check_mode=False
    )

    if not HAS_PYHP:
        safe_fail(module, msg='There was a problem loading from the pyhpecw7 '
                  + 'module.', error=str(ie))

    hostname = socket.gethostbyname(module.params['hostname'])
    username = module.params['username']
    password = module.params['password']
    port = module.params['port']

    device = HPCOM7(host=hostname, username=username,
                    password=password, port=port, timeout=600)

    src = module.params.get('file')
    dst = module.params.get('local_path')
    proto = "sftp"

    changed = False

    try:
        device.open()
    except ConnectionError as e:
        safe_fail(module, device, msg=str(e),
                  descr='Error opening connection to device.')

    try:
        file_download = FileDownload(device, proto, src, dst)
        file_download.transfer_file()
        changed = True
    except PYHPError as fe:
        safe_fail(module, device, msg=str(fe),
                  descr='Error transferring file.')

    results = {}
    results['source_file'] = file_download.src
    results['destination_file'] = file_download.dst
    results['changed'] = changed

    safe_exit(module, device, **results)

from ansible.module_utils.basic import *
main()
