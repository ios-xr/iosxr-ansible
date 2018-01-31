#!/usr/bin/python
#------------------------------------------------------------------------------
#
#    Copyright (C) 2016 Cisco Systems, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#------------------------------------------------------------------------------

from ansible.module_utils.basic import *
from ansible.module_utils.shell import *
from ansible.module_utils.netcfg import *
from iosxr_common import *
from iosxr import *

DOCUMENTATION = """
---
module: iosxr_upgrade_package
author: Adisorn Ermongkonchai
short_description: Upgrade packages on IOS-XR device.
description:
  - Upgrade IOS-XR packages on the IOS-XR device.
options:
  host:
    description:
      - IP address or hostname (resolvable by Ansible control host) of
        the target IOS-XR node.
    required: true
  username:
    description:
      - username used to login to IOS-XR
    required: true
    default: none
  password:
    description:
      - password used to login to IOS-XR
    required: true
    default: none
  confirm:
    description:
      - make sure user really want to reload
    required: true
    value: "yes" or other string
  version:
    description:
      - new software version
    required: true
  pkgpath:
    description:
      - souce directory for the package(s)
        Example:
          sftp://user@server/directory/
          ftp://user@server/directory/
          scp://user@server/directory/
          tftp://server/directory/
          http://server/directory/
          https://server/directory/
    required: true
  pkgname:
    description:
      - IOS-XR software packages
        e.g. xrv9k-ospf-1.0.0.0-r61102I.x86_64.rpm
    required: false
    default: none
"""

EXAMPLES = """
- iosxr_upgrade_package:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    version: 6.1.1
    confirm: yes
    pkgpath: "https://secure_server_name"
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

# check if another install command in progress
def is_legacy_iosxr(module):
    command = "show version"
    response = execute_command(module, command)
    return "Build Information:" not in response[0]

# check if another install command in progress
def is_install_in_progress(module):
    command = "show install request"
    response = execute_command(module, command)
    return "No install operation in progress" not in response[0]

def main():
    module = get_module(
        argument_spec = dict(
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            version = dict(required=True, default=None),
            confirm = dict(required=True),
            pkgpath = dict(required=True, default=None),
            pkgname = dict(required=False, default=""),
        ),
        supports_check_mode = False
    )
    args = module.params
    version = args['version']
    pkg_path = args['pkgpath']
    pkg_name = args['pkgname']

    # confirm upgrade
    if args['confirm'] != 'yes':
        module.fail_json(msg='upgrade aborted')

    # cannot run on classic XR
    if is_legacy_iosxr(module):
        module.fail_json(msg='this upgrade module cannot run on 32-bit IOS-XR')

    # make sure no other install in progress
    if is_install_in_progress(module):
        module.fail_json(msg='other install operation in progress')

    # ignore timeout
    module.connection.shell.shell.settimeout(None)

    # run install upgrade command
    command = ('install upgrade source ' +
               pkg_path + ' version ' + version + ' ' + pkg_name + '\n')
    module.connection.shell.shell.send(command)

    response = ''
    prompt = re.compile(r'[\r\n]?[\w+\-\.:\/\[\]]+(?:>|#)')
    ask = re.compile(r'[\r\n]?\[yes\/no]:\[\w+]\s')

    # wait for either command prompt or activate prompt
    while True:
        try:
            response += module.connection.shell.shell.recv(1024)

            # if activate prompt then send yes
            if ask.search(response):
                module.connection.shell.shell.send('yes\n')
                break

            # if command prompt then it probably is error response
            elif prompt.search(response):
                if 'aborted' in response:
                    module.fail_json(msg=response)
                break
        except:
            break

    # now wait till reload
    while True:
        try:
            #  install operation done
            if not is_install_in_progress(module):
                break
            sleep(5)
        # or socket exception when reload
        except:
            break

    # show result
    result = dict(changed=True)
    result['stdout'] = response
    result['stdout_lines'] = str(result['stdout']).splitlines()

    module.exit_json(**result)

if __name__ == "__main__":
    main()
