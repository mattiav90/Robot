###################### this list is installed on the backup..   ######################

# update system
sudo apt-get update
sudo apt-get upgrade
sudo reboot
sudo apt install git build-essential


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
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip 
# sudo apt-get install python3.8-dev
sudo pip3 install adafruit-circuitpython-servokit

# find the i2c servo driver
sudo i2cdetect -y -r 1


###################### testiong this stuff   ######################

#install python3.7
sudo apt install python3.7-dev




###################### from here on, you have to figure out what to install...   ######################




# opencv e camera works with 2.7 python
# servo motor and adafruit works with python 3.8. 
# 

# install opencv. this works. but I am not sure which version I am installing it in. 
sudo apt-get install python3-opencv
sudo apt-get remove python3-opencv





# install pip
sudo apt-get install python-pip
# install matplotlib
sudo apt-get install python-matplotlib







# install pip. update pip.
cd ~
sudo apt-get install python3-pip
sudo apt install -y python3 git python3-pip

#I managed to isntall cv2 on python3. currently it does not see the camera. do this steps.
sudo apt-get install python3
sudo apt-get install python3-pip
pip3 install --upgrade pip
pip3 install --upgrade setuptools
pip3 install opencv-python






#this might be helpfull to install opoencv on python 3.8. testing it
https://github.com/AastaNV/JEP/tree/master/script







#I managed to install python 3.7.10 using this 
# this will buiuld it from the source. so go in a folder where you can istall it. 
cd ~

sudo apt update
sudo apt install build-essential checkinstall \
    libreadline-gplv2-dev libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
    libffi-dev zlib1g-dev wget

wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz

tar -xzf Python-3.10.12.tgz
cd Python-3.10.12

./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

python3.10 --version

# set as default
echo "alias python3=python3.10" >> ~/.bashrc
source ~/.bashrc





# install opencv from source. this might be the only way if you install python more than 3.8.
sudo apt-get install python3-opencv
# this might br helpfull. 
https://qengineering.eu/install-opencv-on-jetson-nano.html
