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
pip install FaBoPWM-PCA9685-Python/
#then use the code in the file test_steer.py


########## create a virtual environment  ##########




###################### this is correct and it works only with python 3.7 at least. ######################
# I need this to test the servo motors.

# install python3.8 and set up 2 alternatives.
sudo apt install -y python3.8
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python2.7 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 3
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 4
# this command lets you select which python to use in automatic (version)
sudo update-alternatives --config python3



# install adaftruit for pwm. for this you need at least python3.7. or blinka will complain

#install pip and pip3. and update it. 
sudo apt-get install python-pip
sudo apt-get install python3-pip
sudo pip install --upgrade pip 
sudo pip3 install --upgrade pip 


# sudo apt-get install python3.8-dev
sudo pip3 install adafruit-circuitpython-servokit

# find the i2c servo driver
sudo i2cdetect -y -r 1


###################### testiong this stuff   ######################

# FaBoPWM-PCA9685-Python
#use the PCA9685 board with 12C.
#### install

git clone https://github.com/FaBoPlatform/FaBoPWM-PCA9685-Python
pip install FaBoPWM-PCA9685-Python/




###################### from here on, you have to figure out what to install...   ######################



