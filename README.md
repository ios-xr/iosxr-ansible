# Introduction to IOS-XR Ansible

In the nutshell, Ansible is an automation tool for configuring system,
deploying software, and orchestrating services. Unlike Puppet and Chef which
is an agent-based architecture, Ansible does not require daemon running or
agent pre-installed on the target nodes to interact with the Ansible server.
Ansible could be specified to run either on **local** server or on **remote**
node.

The different between local and remote connection mode in Ansible is basically
where the script (so-called Ansible module) is being run.  For the remote mode,
Ansible automatically attempts to establish SSH connection to the remote node.
Once established, it transfers the script and runs it on the remote node.
The script responds to the server in JSON formatted text. This mode requires
setting up third-party namespace (TPNNS) on the IOS-XR node.

As for the local mode, Ansible run the module script on the local server.
The script has to establish a connection to the remote node itself. The
local mode module uses Ansible network module to establish SSH connection
to the IOS-XR console to run CLI command.

There are 2 implementions of local mode, CLI and NECONF XML. And there are 2
options for NETCONF XML, raw and YDK options. The YDK option requires ydk-py
python libraries from github.

There are 6 different ways to access IOS-XR in local mode.
1.	**Console CLI** - connect to IOS-XR console through SSH port 22 and use
                  CLI commands.
2.	**TPNNS CLI** - connect to IOS-XR Linux shell through SSH port 57722
                  and use helper programs, /pkg/bin/xr_cli or /pkg/sbin/config.
3.	**Raw XML** - connect to IOS-XR console through SSH port 22 to exchange XML
                  construct with IOS-XR xml agent.
4.	**Raw NETCONF 1.0** - connect to IOS-XR console through SSH port 22 to
                  exchange NETCONF 1.0 XML construct with IOS-XR netconf agent.
5.	**Raw NETCONF 1.1** - connect to IOS-XR console through SSH port 830 to
                  exchange NETCONF 1.1 XML construct with IOS-XR netconf-yang
                  agent.
6.	**YDK NETCONF** - use the Cisco YDK API service to manage IOS-XR device
                  through SSH port 830.

Managing the IOS-XR device in the remote mode required TPNNS through SSH
port 57722 with the helper programs, /pkg/bin/xr_cli and /pkg/sbin/config, to
deliver CLI commands and configuration to the IOS-XR, respectively.  This
remote mode connection is identical to TPNNS CLI running in local mode except
for how the SSH connection is being established and where the script is run.

# Understand connection variants
With different variants for local and remote modes mentioned earlier, before
implementing Ansible modules, one needs to be aware of their limitation.
-	**Linux-based vs. QNX-based IOS-XR**
  * QNX-based IOS-XR can only run in local mode
  * Earlier version of Linux-based IOS-XR also can only run in local mode due
    to incomplete Python libraries
  * Linux-based IOS-XR (eXR 6.0.2 or later) can run both remote and local modes
-	**CLI vs. XML/NETCONF**
  * With CLI mode, you can do all CLI commands as you would do interactively.
  * The XML/NETCONF mode allows you to use Cisco XML or NETCONF commands in XML
    construct to configure IOS-XR.
-	**Console CLI vs. TPNNS CLI**
  * Console CLI allows you to do all CLI commands as you would do interactively.
  * TPNNS CLI can either be implemented in local or remote mode.  It connects
    to IOS-XR Linux shell and requires helper programs, /pkg/bin/xr_cli or
    /pkg/sbin/config, to deliver CLI commands or configure IOS-XR, respectively.
    Currently, "commit replace" is not supported by /pkg/sbin/config.
-	**Raw XML/NETCONF vs. YDK NETCONF**
  * Raw NETCONF mode allows you to configure IOS-XR using NETCONF commands in
    RPC XML construct through standard SSH port 22 with termination sequence
    **]]>]]>** and port 830 with **##** termination sequence.  The response is
    also in RPC XML construct.
  * Alternatively, you can use YDK python API to configure IOS-XR through SSH
    port 830.  The API automatically generates the RPC XML construct based on
    the YANG model provided.
    
**NOTE:** IOS-XR NETCONF 1.1 XML construct is based on Cisco IOS-XR YANG model 
      which is currently limited, e.g. it doesn’t support SMU package 
      installation.  Although limited, the Cisco IOS-XR YANG definitions will
      continue to grow as more definitions are added and would be a preferred
      method for accessing IOS-XR. 

# Ansible Test Setup

- **Prerequisite**
  * Create 2 XRV9K (Sunstone) VM's with k9sec security package
  * 1 Linux server
  * Create network connection between XRV9K and Linux server

- Pull YDK from the github into the Linux server
  * git clone https://github.com/CiscoDevNet/ydk-py

- Pull Ansible Core modules
  * git clone git://github.com/ansible/ansible.git --recursive

  Addition read on Ansible installation is here
  * http://docs.ansible.com/ansible/intro_installation.html#getting-ansible

# Directories structure

```
iosxr-ansible
├── local
│   ├── library
│   ├── samples
│   │   ├── cli
│   │   ├── tpnns
│   │   ├── xml
│   │   └── ydk
│   └── common
└── remote
    ├── library
    └── samples
        └── test

Directory               Description

local/library           Contains Ansible modules for local mode
local/samples/cli       Contains sample playbooks using Console CLI
local/samples/tpnns     Contains sample playbooks using TPNNS access method
local/samples/xml       Contains sample RPC XML used with iosxr_netconf_send
local/samples/ydk       Contains sample playbooks using YDK API's
local/common            Contains IOS-XR common Python functions
remote/library          Contains Ansible modules for remote mode
remote/samples          Contains sample playbooks using Namespace Shell CLI
remote/samples/test     Contains additional playbooks showing direct access
                        to IOS-XR using shell
```

# IOS-XR setup

NOTE: Some of these instruction may require root access for setting IOS-XR.

- Create default crypto key on your XRV9K VMs (select default 2048 bits)

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
  RP/0/RP0/CPU0:ios(config)# xml agent tty
  RP/0/RP0/CPU0:ios(config)# netconf agent tty
  RP/0/RP0/CPU0:ios(config)# netconf-yang agent ssh
  RP/0/RP0/CPU0:ios(config)# commit
```
- Optional SSH key setup allows user to connect to IOS-XR without password.
  First, generate base64 SSH key file on Ansible Server and copy it to your
  tftpboot directory.

```
  cut -d" " -f2 ~/.ssh/id_rsa.pub | base64 -d > ~/.ssh/id_rsa_pub.b64
  cp ~/.ssh/id_rsa_pub.b64 /tftpboot
```
- After IOS-XR is ready, at IOS-XR console prompt, import SSH key as followed

```
  RP/0/RP0/CPU0:ios# crypto key import authentication rsa tftp://192.168.1.1/id_rsa_pub.b64
  RP/0/RP0/CPU0:ios# show crypto key authentication rsa
```
- Now make sure you can connect to both XRV9K VMs management port from Linux host

```
  ssh cisco@192.168.1.120
  ssh cisco@192.168.1.120 "show run"
```

- Set third party namespace (TPNNS) access on IOS-XR.  Please refer to the
  following link for instruction and make sure you can SSH to the IOS-XR
  through port **57722**.
  
    http://www.cisco.com/c/en/us/td/docs/iosxr/AppHosting/b-application-hosting-configuration-guide/AH_User_Guide_chapter_00.html

    To access IOS-XR without password, you will also need to add your 
    Linux server SSH public key (~/.ssh/id_rsa.pub) to your IOS-XR
    \<your_xr_home\>/.ssh/authorized_key file by using **ssh-copy-id**
    command, for example,

```
  ssh-copy-id -i ~/.ssh/id_rsa.pub -p 57722 cisco@192.168.1.120
```

- If your Linux server support HTTPS, you may also want to import the
  certificate from Linux to IOS-XR so that you can install new SMU package.
  The IOS-XR certificate store is in /etc/ssl/certs/ca-certificates.crt.
  Basically, you just need to cut and paste your certificate to this file.
  
# Local mode setup and test

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
  192.168.1.120 ansible_ssh_user=cisco
  192.168.1.121 ansible_ssh_user=cisco
```
- Run sample playbooks
    * Some of sample playbooks will require changes to fit your need
      e.g. edit iosxr_install_package.yml to change location of your package.

```
  cd samples
  ansible-playbook iosxr_get_config.yml
  ansible-playbook iosxr_clear_log.yml
  ansible-playbook iosxr_cli.yml -e 'cmd="show interface brief"'
  ansible-playbook iosxr_netconf_send.yml -e "xml_file=xml/nc_show_install_active.xml"
```
# Remote mode setup and test

- Configure Ansible configuration to use port 57722 by editing your ansible
  config file (default is /etc/ansible/ansible.cfg) with following values
    
```
    [defaults]
    remote_port = 57722
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
  192.168.1.120 ansible_ssh_user=cisco
  192.168.1.121 ansible_ssh_user=cisco
```
- Run sample playbooks
    * Some of sample playbooks will require changes to fit your need
      e.g. edit iosxr_install_package.yml to change location of your package.

```
  cd samples
  ansible-playbook iosxr_get_config.yml
  ansible-playbook iosxr_cli.yml -e 'cmd="show interface brief"'
```
# IOS-XR platforms tested
- XRv9K (sunstone)
- ASR9K (classic 32-bit QNX IOS-XR)
- NCS5500 (fretta)
- NCS1000 (Rosco) - tested by Rosco team
