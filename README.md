## Ansible Test Setup

- **Prerequisite**
  * Create 2 XRV9K (Sunstone) VM's with k9sec security package
  * 1 Linux server
  * Create network connection between XRV9K and Linux server

- Pull YDK from the github into the Linux server
  * git clone https://github.com/CiscoDevNet/ydk-py

- Pull Ansible Core modules
  * git clone git://github.com/ansible/ansible.git --recursive

  Addition read on Ansible installation is here
  * http://docs.ansible.com/ansible/intro_installation.html#getting-ansible

## Local vs. Remote

The different between local and remote mode in Ansible is basically
where the script is being run.  For the remote mode, Ansible automatically
attempts to establish SSH connection to the remote node.  Once established,
it copies a script, so-called Ansible module, and runs it on the remote
node. The script responds to the server in JSON format. This mode requires
TPNNS running on the IOS-XR node (see earlier section on TPNNS setup)

As for the local mode, Ansible run the module script on the local server.
The script has to establish a connection to the remote node itself. The
"local" IOS-XR Ansible module uses Ansible core network module to connect
to IOS-XR console to run CLI command.

There are 2 implementions of "local" mode, CLI and Netconf. There are 2
options for Netconf, raw or YDK option. YDK option requires ydk-py
python libraries from github.

## Directories structure

```
iosxr-ansible
├── local
│   ├── library
│   ├── samples
│   │   ├── cli
│   │   ├── vars
│   │   ├── xml
│   │   └── ydk
│   └── xrapi
└── remote
    ├── library
    └── samples
        └── test

Directory               Description

local/library           Contains Ansible modules for local mode
local/samples/cli       Contains sample playbooks using Console CLI
local/samples/vars      Contains common variables used by the playbooks
local/samples/xml       Contains sample RPC XML used with iosxr_netconf_send
local/samples/ydk       Contains sample playbooks using YDK API's
local/xrapi             Contains common Python functions
remote/library          Contains Ansible modules for remote mode
remote/samples          Contains sample playbooks using TPNNS CLI
remote/samples/test     Contains additional playbooks showing direct access
                        to IOS-XR using shell
```

## IOS-XR setup

- Create default crypto key on your XRV9K VMs (select default 1024 bits)

```
  RP/0/RP0/CPU0:ios# crypto key generate rsa 
  RP/0/RP0/CPU0:ios# show crypto key mypubkey rsa
```
- Configure IOS-XR as shown in ss1.cfg and ss2.cfg for both XRV9K VMs.
  Make any necessary changes, such as, management IP address and hostname
  Here are required configuration
  
```
  RP/0/RP0/CPU0:ios# conf t
  RP/0/RP0/CPU0:ios(config)# ssh server v2
  RP/0/RP0/CPU0:ios(config)# ssh server netconf vrf default
  RP/0/RP0/CPU0:ios(config)# ssh server logging
  RP/0/RP0/CPU0:ios(config)# xml agent ssl
  RP/0/RP0/CPU0:ios(config)# netconf agent tty
  RP/0/RP0/CPU0:ios(config)# netconf-yang agent ssh
  RP/0/RP0/CPU0:ios(config)# commit
```
- Make sure you can connect to both XRV9K VMs management port from Linux host

```
  ssh root@192.168.1.120
  ssh root@192.168.1.120 "show run"
```
  > NOTE:
  > Currently, crypto key import is not working (CSCuy80921) so when
  > using Ansible playbook, password is required.

## Local mode setup and test

- Edit and source Ansible, YDK, and Python environment to point to your
  installed applications

```
  cd iosxr-ansible/local
  vi ansible_env
  source ansible_env
```
- Edit "ansible_hosts" file to change "ss-xr" host IP to your 2 XRV9K VMs

```
  [ss-xr]
  192.168.1.120
  192.168.1.121
```
- Run sample playbooks
    * Before running sample playbook, you will want to edit the file
      iosxr-ansible/local/samples/vars/iosxr_vars.yml to assign username and
      password for your IOS-XR.
  
    * In addition, you will want to edit these playbooks to your need,
      e.g. iosxr_install_smu.yml and iosxr_user_add.yml, ## Local vs. Remote

```
  cd samples
  ansible-playbook iosxr_get_config.yml
  ansible-playbook iosxr_clear_log.yml
  ansible-playbook iosxr_cli.yml -e 'cmd="show interface brief"'
  ansible-playbook iosxr_netconf_send.yml -e "xml_file=xml/nc_show_install_active.xml"
```
## Remote mode setup and test

Additional steps are required for setting up XR for use with Ansible in
"remote" mode.

- After IOS-XR is ready, at IOS-XR console prompt, enter following commands

```
  RP/0/RP0/CPU0:ios# run sed -i.bak -e '/^PermitRootLogin/s/no/yes/' /etc/ssh/sshd_config_tpnns
  RP/0/RP0/CPU0:ios# run service sshd_tpnns restart
  RP/0/RP0/CPU0:ios# run chkconfig --add sshd_tpnns
```
- You also need to add your Linux server ssh public key from your
  ~/.ssh/id_rsa.pub to IOS-XR authorized_key file
  
```
  cat ~/.ssh/id_rsa.pub
  ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDeyBBEXOyWd/8bL4a/hwEZnOb7vgns
  vh6jRgsJxNTMrF+NWkeknhXyzT48Wt3bU9Dxtq++unWoIkfOktcK6dVzVk0wrZ/PA64Z
  c3vVpKPx22AIidwyegSVWtCXuv7C1V19gCRg1uddPSRtBbQ6uYjJylu1V9NzJYL4fDts
  XJiepyyohGLYj+fHHPMdO6LZmGVhEqlLGl4cqRPsD3D7zzxIag9E/7CVPGiA+0fVvGOq
  n7BL0x62bdcSzKDZUT3A0NGqht2RcEnYH7WQjzG3ikw230aiqBBr75LNzVkMxHZr8Mf6
  Mr5iHcbAyGyjoDKxNA1LoAu6wGgQ4Gg66fr1U8bN aermongk@ansible-dev
```

```
  RP/0/RP0/CPU0:ios# run vi /root/.ssh/authorized_keys
```
- Testing TPNNS on XR by ssh to XR management address on port 57722

```
  ssh -p 57722 root@192.168.1.120
  ssh -p 57722 root@192.168.1.120 ifconfig
  ssh -p 57722 root@192.168.1.120 nsenter -t 1 -n -- ifconfig
```
  > NOTE:
  > "nsenter" is part of the util-linux package which allows program to
  > be running in other process namespace.  In the example, notice that
  > the "ifconfig" returns different interfaces that is because the second
  > one is run in "init" process namespace.

- Configure Ansible configuration to use port 57722 and connect to "root" user
  * edit your ansible config file (default is /etc/ansible/ansible.cfg) with
    following values
    
```
    [defaults]
    remote_port = 57722

    [ssh_connection]
    ssh_args = -o "User=root"
```
- Edit Ansible and Python environment as needed in ansible_env and source it

```
  cd iosxr-ansible/remote
  vi ansible_env
  source ansible_env
```
- Edit "ansible_hosts" file to change "ss-xr" host IP to your 2 XRV9K VMs

```
  [ss-xr]
  192.168.1.120
  192.168.1.121
```
- Run sample playbooks

```
  cd samples
  ansible-playbook iosxr_get_config.yml
  ansible-playbook iosxr_cli.yml -e 'cmd="show interface brief"'
```