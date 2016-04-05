Ansible Test Setup
==================

- Create 2 XRV9K (Sunstone) VMs and 1 Linux server on MB Cloud following
  the instruction in the link below
  * http://tc-midnight.cisco.com:8080/wiki/MB%20Cloud%20XR

  NOTE:
    The nightly build images provided on the MB Cloud is based on xr-dev lineup.
    Unfortunately, the missing Python libraries were committed only to r60y
    (CSCux90222).  These missing libraries are required for Ansible to run
    in "remote" mode. The playbooks under "local" directory use local mode and
    playbooks under "remote" use remote mode.  If you want to run playbooks
    under "remote" directory, you will need to build your own XRV9K image from 
    r60y lineup and install it on your VMs.

- You will also need k9sec security package to be installed in your XRV9K VMs.
  Using the following example command to install the k9sec pacakge.
  * install update source tftp://192.168.1.1 xrv9k-iosxr-security-1.0.0.0-r60125I
  * show install active

- Pull YDK from the github into the Linux server created
  * git clone https://github.com/CiscoDevNet/ydk-py

- Pull Ansible Core modules
  * git clone git://github.com/ansible/ansible.git --recursive

  Addition read on Ansible installation is here
  * http://docs.ansible.com/ansible/intro_installation.html#getting-ansible

Running Ansible
===============

- Edit and source Ansible, YDK, and Python environment to point to your
  installed applications
  * cd iosxr/local
  * vi ansible_env
  * source ansible_env

- Edit "ansible_hosts" file to change "ss-xr" host IP to your 2 XRV9K VMs

- Create default crypto key in your XRV9K VMs (select default 1024 bits)
  * crypto key generate rsa 
  * show crypto key mypubkey rsa

- Configure IOS-XR as shown in ss1.cfg and ss2.cfg for both XRV9K VMs.
  Make any necessary changes, such as, management IP address and hostname
  Here are required configuration
  * ssh server v2
  * ssh server netconf vrf default
  * ssh server logging
  * xml agent ssl
  * netconf agent tty
  * netconf-yang agent ssh
  
- Make sure you can connect to both XRV9K VMs management port
  * ssh root@x.x.x.x
  * ssh root@x.x.x.x "show run"

  NOTE:
    Currently, crypto key import is not working (CSCuy80921) so when
    using Ansible playbook, password is required.

Remote mode setup
=================

- Additional steps are required to setup XR for use with Ansible in "remote"
  mode.  As mentioned earlier, it will also require IOS-XR image with correct
  Python Libraries installed
  On IOS-XR console prompt, enter following commands
  * run sed -i.bak -e '/^PermitRootLogin/s/no/yes/' /etc/ssh/sshd_config_tpnns
  * run service sshd_tpnns restart
  * run chkconfig --add sshd_tpnns

- Testing TPNNS on XR by ssh to XR management address on port 57722
  * ssh -p 57722 root@x.x.x.x
  * ssh -p 57722 root@x.x.x.x ifconfig
  
- Configure Ansible to use port 57722
  * edit your ansible config file (default is /etc/ansible/ansible.cfg) with
    following values
    
    [defaults]
    remote_port = 57722
    [ssh_connection]
    ssh_args = -o "User=root"
  

Additional Notes
================

- How to GitLab?
  * https://cisco.jiveon.com/docs/DOC-42998