# -*- mode: ruby -*-
# vi: set ft=ruby :


# This is a script of shell commands run at "provision" time by Vagrant.
# It could just as easily be within the "provision" stanza below, but
# this was the structure of an example file I first got to work
# and I kept this style.

$provision_script = <<'EOF'
echo "shell provisioning"

# Just some logging to timestanp the last provisioning time
PROVISIONED_ON=/etc/vm_provision_on_timestamp

# virtualbox appears to be horribly bufferbloated or something.
# Let's try enabling fq_codel to see if that helps...
sudo echo "net.core.default_qdisc=fq_codel" > /etc/sysctl.d/60-debloat.conf
sudo sysctl -p

# get the latest-and-greatest bug-fixes from the mothership
sudo apt-get update
# Uncomment this to update the whole shebang
#sudo apt-get -y dist-upgrade

# These are the packages we actually care need. They will bring in a whole raft of dependencies.
sudo apt-get install -y python-scipy git python-pip fftw3 fftw3-dev liblapack-dev libblas-dev gfortran libgeos-3.5.0 libgeos-dev ipython-notebook

# This is where we specify Python specific things that aren't packaged by Ubuntu

# I forget what needs this
pip install future

# This appears to need a login, which is a pain for the demo; Let's just use the older ipython-notebook ubuntu package above
#pip install jupyter

# This is the central package for our work. The Python binding of the SHTools spherical harmonics toolkit.
pip install pyshtools

# The xenial package of basemap has a serious bug that prevents Molleweide map projections from working; fixed in git.
pip install matplotlib
pip install git+https://github.com/matplotlib/basemap.git

# Tag the provision time:
date > "$PROVISIONED_ON"

echo "Successfully created Spherical Harmonic Code virtual machine."
echo ""

EOF

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.

  # The bento boxes seem to have more attention paid to Vagrant/VirtualBox requirements
  # than the vanilla Ubuntu boxes. Uncomment to use this box.
  #config.vm.box = "bento/ubuntu-16.04"

  # This is a recently packaged box that has a good reputation for coming straight up
  config.vm.box = "geerlingguy/ubuntu1604"

  # This is Ubuntu's vanilla box. I had lots of trouble with it.
  #config.vm.box = "ubuntu/yakkety64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # This is a port for the IPython/Jupyter notebook server; Connect to localhost:8888 from the host...
  config.vm.network "forwarded_port", guest: 8888, host: 8888, auto_correct: true
 
  # This is a port normally used by a Postgresql server. Not needed for this demo project.
  #config.vm.network "forwarded_port", guest: 5432, host: 15432, auto_correct: true
 
  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # This caused all kinds of pain because it wanted to establish an ethernet device
  # named in the old-style form of eth1  That of course has now been "improved"
  # by systemd. Uncommenting this prevents vagrant from installing a clean machine.
  # Grrrrrrrrrr. systemd. GRRRRRRRRRRRR.
  #config.vm.network "private_network", ip: "192.168.33.11"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # A possible source of similar pain from systemd as in the private network stanza above.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # The synced folder /vagrant is supposed to be automagically created.
  # It did not work correctly for me in an earlier Vagrant project, so I'm keeping this
  # here but commented out.
  #config.vm.synced_folder "./", "/vagrant"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    # vb.gui = true
    
    # Customize the amount of memory on the VM:
    # Tweak to suit your host machine and problem requirements.
    vb.memory = "6144"

    # Give the virtual machine 2 cores to play with:
    # Also tweak to suit your host machine and problem requirements.
    vb.cpus = 2
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # This is only useful if you intend to push your configured box to Atlas. 
  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end
  
  
  # we will try to autodetect this path. 
  # However, if we cannot or you have a special one you may pass it like:
  # config.vbguest.iso_path = "#{ENV['HOME']}/Downloads/VBoxGuestAdditions.iso"
  # or
  # config.vbguest.iso_path = "http://company.server/VirtualBox/%{version}/VBoxGuestAdditions.iso"

  # set auto_update to false, if you do NOT want to check the correct 
  # additions version when booting this machine
  config.vbguest.auto_update = false

  # do NOT download the iso file from a webserver
  config.vbguest.no_remote = true

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # This is where the shell script at the top of this file gets executed by inclusion.
  config.vm.provision :shell, :inline => $provision_script
  
  # Fire off the Ipython notebook server
  # Because of the run always config, this stanza is executed even when
  # you are not running "vagrant provision". We are using this run the notebook server
  config.vm.provision :shell, run: "always", inline: <<-SHELL
    ipython notebook --notebook-dir=/vagrant --no-browser --ip=0.0.0.0 &
  SHELL

end
