######################   this list is installed on the backup	######################

#######################	all of this stuff should be also in the backup	#######################

# update system
sudo apt-get update
sudo apt-get upgrade
sudo reboot
sudo apt install git build-essential
sudo apt install software-properties-common


#install support for exfat drives
sudo apt install git build-essential
cd ~
git clone https://github.com/arter97/exfat-linux
cd exfat-linux
make
sudo make install
sudo reboot
sudo modprobe exfat
cat /proc/filesystems


# install code-oss (editor)
sudo apt-get install curl
curl -L https://github.com/toolboc/vscode/releases/download/1.32.3/code-oss_1.32.3-arm64.deb -o code-oss_1.32.3-arm64.deb
sudo dpkg -i code-oss_1.32.3-arm64.deb

#setup github
git config --global user.email "mattia.vezzoli@yale.edu"
git config --global user.name "mattiav90"


# avoid to enter password all the time when running sudo commands
sudo visudo
# add this at the end of the file
mattiav90 ALL=(ALL) NOPASSWD: ALL


# installing fan
git clone https://github.com/Pyrestone/jetson-fan-ctl.git
cd jetson-fan-ctl
sudo ./install.sh


#push and pull ingithub with no passoword. setup a key.
ssh-keygen -t ed25519 -C "mattia.vezzoli@yale.edu"
eval "$(ssh-agent -s)" ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
# go in local repo to run this
git remote set-url origin git@github.com:mattiav90/Robot.git



###### install package for steering servo ########

# follow this: https://github.com/FaBoPlatform/FaBoPWM-PCA9685-Python

git clone https://github.com/FaBoPlatform/FaBoPWM-PCA9685-Python
sudo apt-get install python3-pip
pip3 install FaBoPWM-PCA9685-Python/
#then use the code in the file test_steer.py


########## configure th 40 pin of jetson nano  ##########

$ sudo /opt/nvidia/jetson-io/jetson-io.py
configure manually
activate pwm0 and pwm2

# Enable Pin 32 / PWM0
busybox devmem 0x700031fc 32 0x45
busybox devmem 0x6000d504 32 0x2

# Enable Pin 33 / PWM2
busybox devmem 0x70003248 32 0x46
busybox devmem 0x6000d100 32 0x00


## setting up the vnc

#Enable the VNC server to start each time you log in
#If you have a Jetson Nano 2GB Developer Kit (running LXDE)
mkdir -p ~/.config/autostart
cp /usr/share/applications/vino-server.desktop ~/.config/autostart/.

#Configure the VNC server
gsettings set org.gnome.Vino prompt-enabled false
gsettings set org.gnome.Vino require-encryption false

#Set a password to access the VNC server
# Replace thepassword with your desired password
gsettings set org.gnome.Vino authentication-methods "['vnc']"
gsettings set org.gnome.Vino vnc-password $(echo -n 'tripleh'|base64)

#Reboot the system so that the settings take effect
sudo reboot

#The VNC server is only available after you have logged in to Jetson locally. If you wish VNC to be available automatically, use the system settings application on your developer kit to enable automatic login.



# to use the vnc with jetson nano and connect from it remotely, we have to fake that there is a
# screen connected to it. otherwise the resolution is 640.
# do this:

Setting the Desktop Resolution

The desktop resolution is typically determined by the capabilities of the
display that is attached to Jetson. If no display is attached, a default
resolution of 640x480 is selected. To use a different resolution, edit
/etc/X11/xorg.conf and append the following lines:

Section “Screen”
Identifier “Default Screen”
Monitor “Configured Monitor”
Device “Tegra0”
SubSection “Display”
Depth 24
Virtual 1600 1200 # Modify the resolution by editing these values
EndSubSection
EndSection


# to install the joypad drivers use: 
pip3 install pygame

#also you have to set this variable in the terminal to dont get it to complain:
export DBUS_FATAL_WARNINGS=0

#also install this software to see if the joystick is connected or not. 
#once installed go find it into the programs user interface. 
# jstest-gtk. 
sudo apt-get install jstest-gtk 



#then just ask chatgpt to write a simple program to use the joystick with this library.


