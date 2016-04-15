Ansible Test Setup
==================

- Prerequisite:
  * Create 2 XRV9K (Sunstone) VM's with k9sec security package from r60y
  * 1 Linux server
  * Create network connection between XRV9K and Linux server

  NOTE:
    The reason for using r60y because it has more complete Python libraries
    (CSCux90222).  These missing libraries are required for Ansible to run
    in "remote" mode. The playbooks under "local" directory use local mode and
    playbooks under "remote" use remote mode.  You can get the r60y image
    xrv9k-fullk9-x.iso-R60Y-xx.xx.xxx from the following nightly build
    directory, /auto/ioxdepot4/r60y/all/nightly_image_dir.

- Pull YDK from the github into the Linux server
  * git clone https://github.com/CiscoDevNet/ydk-py

- Pull Ansible Core modules
  * git clone git://github.com/ansible/ansible.git --recursive

  Addition read on Ansible installation is here
  * http://docs.ansible.com/ansible/intro_installation.html#getting-ansible

Setup Ansible and IOS-XR
========================

- Edit and source Ansible, YDK, and Python environment to point to your
  installed applications
  * cd <ws>/iosxr-ansible/local
  * vi ansible_env
  * source ansible_env

- Edit "ansible_hosts" file to change "ss-xr" host IP to your 2 XRV9K VMs

- Create default crypto key on your XRV9K VMs (select default 1024 bits)
  * RP/0/RP0/CPU0:ios# crypto key generate rsa 
  * RP/0/RP0/CPU0:ios# show crypto key mypubkey rsa

- Configure IOS-XR as shown in ss1.cfg and ss2.cfg for both XRV9K VMs.
  Make any necessary changes, such as, management IP address and hostname
  Here are required configuration
  * RP/0/RP0/CPU0:ios# conf t
  * RP/0/RP0/CPU0:ios(config)# ssh server v2
  * RP/0/RP0/CPU0:ios(config)# ssh server netconf vrf default
  * RP/0/RP0/CPU0:ios(config)# ssh server logging
  * RP/0/RP0/CPU0:ios(config)# xml agent ssl
  * RP/0/RP0/CPU0:ios(config)# netconf agent tty
  * RP/0/RP0/CPU0:ios(config)# netconf-yang agent ssh
  * RP/0/RP0/CPU0:ios(config)# commit
  
- Make sure you can connect to both XRV9K VMs management port from Linux host
  * ssh root@x.x.x.x
  * ssh root@x.x.x.x "show run"

  NOTE:
    Currently, crypto key import is not working (CSCuy80921) so when
    using Ansible playbook, password is required.

Remote mode setup
=================

- Additional steps are required for setting up XR for use with Ansible in
  "remote" mode.  As mentioned earlier, it will also require IOS-XR image
  with correct Python Libraries installed

  After IOS-XR is ready, at IOS-XR console prompt, enter following commands
  * RP/0/RP0/CPU0:ios# run sed -i.bak -e '/^PermitRootLogin/s/no/yes/' /etc/ssh/sshd_config_tpnns
  * RP/0/RP0/CPU0:ios# run service sshd_tpnns restart
  * RP/0/RP0/CPU0:ios# run chkconfig --add sshd_tpnns

- Testing TPNNS on XR by ssh to XR management address on port 57722
  * ssh -p 57722 root@x.x.x.x
  * ssh -p 57722 root@x.x.x.x ifconfig
  * ssh -p 57722 root@x.x.x.x nsenter -t 1 -n -- ifconfig
    or
    ssh -p 57722 root@x.x.x.x ip netns exec default ifconfig
  
  NOTE: "nsenter" is part of the util-linux package which allows program to
        be running in other process namespace.  In the example, notice that
        the "ifconfig" returns different interfaces that is because the second
        one is run in "init" process namespace.  Alternative to using "nsenter",
        you can use "ip netns" command to do the same thing.  The "default"
        namespace used by "ip netns" is defined in /var/run/netns.

- Edit Ansible and Python environment as needed in ansible_env and source it
  * cd <ws>/iosxr-ansible/remote
  * vi ansible_env
  * source ansible_env
  
- Configure Ansible configuration to use port 57722 and connect to "root" user
  * edit your ansible config file (default is /etc/ansible/ansible.cfg) with
    following values
    
    [defaults]
    remote_port = 57722

    [ssh_connection]
    ssh_args = -o "User=root"
  
Local VS. Remote
================

The different between local and remote mode in Ansible is basically
where the script is being run.  For the remote mode, Ansible automatically
attempts to establish ssh connection to the remote node.  Once established,
it copies the script, so-called Ansible module, and runs it on the remote
node. The script responses to the server in json format. This mode requires
TPNNS running on the IOS-XR node (see earlier section on TPNNS setup)

As for the local mode, Ansible run the module script on the local server.
The script has to establish a connection to the remote node itself. The
"local" IOS-XR Ansible module uses Ansible core network module to connect
to IOS-XR console to run CLI command.

There are 2 implementions of "local" mode, CLI and Netconf. There are 2
options for Netconf, raw or YDK option. YDK option requires ydk-py
python libraries from github.

Directories structure
=====================

iosxr-ansible
├── local
│   ├── library
│   ├── samples
│   │   ├── cli
│   │   ├── vars
│   |   ├── xml
│   │   └── ydk
│   └── xrapi
└── remote
    ├── library
    └── samples
        └── test

Directory               Description
===============================================================================
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

Additional Notes
================

- You also want to edit the file <ws>/local/samples/vars/iosxr_vars.yml to
  assign username and password for your IOS-XR.

- How to GitLab?
  * https://cisco.jiveon.com/docs/DOC-42998