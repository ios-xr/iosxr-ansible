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

import paramiko
from ansible.module_utils.basic import *

DOCUMENTATION = """
---
module: iosxr_file_copy
author: Adisorn Ermongkonchai
short_description: Copy file to or from IOS-XR /disk0:
description:
  - Copy file to or from IOS-XR /disk0:

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
  path:
    description:
      - local path used in "put" direction only
    required: false
    default: none
  filename:
    description:
      - name of the file
    required: true
    default: none
  direction:
    description:
      - "get" from XR or "put" to XR
    required: true
    default: none
"""

EXAMPLES = """
- iosxr_file_copy:
    host: "{{ ansible_host }}"
    username: "{{ ansible_user }}"
    password: "{{ ansible_ssh_pass }}"
    path: "/scratch/"
    filename: "iosxr_config.txt"
    direction: "put"

- iosxr_file_copy:
    provider:
      host: "{{ ansible_host }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
    filename: "cvac.log"
    direction: "get"
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

def main ():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=True),
            username = dict(required = False, default = None),
            password = dict(required = False, default = None),
            path= dict(required = False, default = "./"),
            filename= dict(required = True, default = None),
            direction= dict(required = True, default = None)
        ),
        supports_check_mode = False
    )
    args = module.params
    host = args["host"]
    username = args["username"]
    password = args["password"]
    path = args["path"]
    filename = args["filename"]
    port = 22
    xrpath = "/disk0:/"

    transport = paramiko.Transport ((host, port))
    transport.connect (username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport (transport)
    sftp.chdir(xrpath)

    result = dict (changed = False)
    try:
        if args["direction"] == "put":
            localpath = path + filename
            sftp.put (localpath, filename)
            result["stdout"] = "successfully put " + filename
        else:
            localpath = path + filename
            sftp.get (filename, localpath)
            result["stdout"] = "successfully get " + filename

    except:
        module.fail_json (msg="file copy failed")

    sftp.close ()
    transport.close ()

    result["changed"] = True
    result["stdout_lines"] = str (result["stdout"]).split (r"\n")
    module.exit_json (**result)

if __name__ == "__main__":
  main ()
