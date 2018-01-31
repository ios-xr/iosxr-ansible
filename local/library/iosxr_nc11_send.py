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
import paramiko

DOCUMENTATION = """
---
module: iosxr_nc11_send
author: Adisorn Ermongkonchai
short_description: Send NETCONF-YANG 1.1 XML file to IOS-XR device
description:
  - Send NETCONF-YANG 1.1 XML file to IOS-XR device
options:
  host:
    description:
      - IP address or hostname (resolvable by Ansible control host) of
        the target IOS-XR node.
    required: true
  username:
    description:
      - username used to login to IOS-XR
    required: false
    default: none
  password:
    description:
      - password used to login to IOS-XR
    required: false
    default: none
  xmlfile:
    description:
      - XML file
    required: true
    example: nc_show_install_active.xml
      <rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <get>
          <filter type="subtree">
            <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"/>
          </filter>
        </get>
      </rpc>
"""

EXAMPLES = """
- iosxr_nc11_send:
    host: '{{ ansible_ssh_host }}'
    username: cisco
    password: cisco
    xmlfile: xml/nc_show_install_active.xml
"""

RETURN = """
stdout:
  description: raw response
  returned: always
stdout_lines:
  description: list of response lines
  returned: always
"""

HELLO = """
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.1</capability>
    </capabilities>
</hello>
]]>]]>"""

COMMIT = """
#91
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <commit/>
</rpc>
##
"""

CLOSE = """
#98
<rpc message-id="102" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <close-session/>
</rpc>
##
"""

def main():
    module = AnsibleModule(
        argument_spec = dict(
            host = dict(required=True),
            username = dict(required=False, default=None),
            password = dict(required=False, default=None),
            xmlfile = dict(required=True),
            port = dict(required=False, type='int', default=830)
        ),
        supports_check_mode = False
    )
    args = module.params
    xml_file = module.params['xmlfile']

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(module.params['host'],
                port=module.params['port'],
                username=module.params['username'],
                password=module.params['password'],
                timeout=10)
    transport = ssh.get_transport()
    channel = transport.open_channel('session')
    channel.invoke_subsystem('netconf')

    # read hello msg
    response = channel.recv(1024)
    while ']]>]]>' not in response:
        response += channel.recv(1024)

    result = dict(changed=False)
    xml_text = open(xml_file).read()
    if 'edit-config' in xml_text or 'delete-config' in xml_text:
        result['changed'] = True
    xml_msg = '\n#' + str(len(xml_text)-1) + '\n' + xml_text + '##\n'

    # send hello followed by contents of xml file
    channel.send(HELLO)
    channel.send(xml_msg)

    # collect all responses 1024 bytes at a time
    response = channel.recv(1024)
    while '##' not in response:
        response += channel.recv(1024)

    # commit changes
    if result['changed']:
        channel.send(COMMIT)

    channel.send(CLOSE)

    result['stdout'] = response
    if 'rpc-error' in response:
        return module.fail_json(msg=response)
    else:
        return module.exit_json(**result)

if __name__ == "__main__":
    main()
