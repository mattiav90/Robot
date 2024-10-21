# update
sudo apt-get update

# opencv e camera works with 2.7 python
# servo motor and adafruit works with python 3.8. 
# 

# install opencv
sudo apt-get install python3-opencv
sudo apt-get remove python3-opencv

# install code-oss (editor)
sudo apt-get install curl
curl -L https://github.com/toolboc/vscode/releases/download/1.32.3/code-oss_1.32.3-arm64.deb -o code-oss_1.32.3-arm64.deb
sudo dpkg -i code-oss_1.32.3-arm64.deb

# download the github repo. 
# create a new ssh key.
git config --global user.email "mattia.vezzoli@yale.edu"
git config --global user.name "mattiav90"


# install pip
sudo apt-get install python-pip
# install matplotlib
sudo apt-get install python-matplotlib


# avoid to enter password all the time when running sudo commands
sudo visudo
# find the line that says %sudo   ALL=(ALL:ALL) ALL. and replace it with 
mattiav90 ALL=(ALL:ALL) NOPASSWD: ALL


# installing fan
git clone https://github.com/Pyrestone/jetson-fan-ctl.git
cd jetson-fan-ctl
sudo ./install.sh


# install pip. update pip.
cd ~
sudo apt-get install python3-pip
sudo apt install -y python3 git python3-pip


# install python3.8 and set up 2 alternatives.
sudo apt install -y python3.8
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
# this command lets you select which python to use in automatic (version)
sudo update-alternatives --config python3


# install opencv
sudo apt-get install python3-opencv
# this might br helpfull. 
https://qengineering.eu/install-opencv-on-jetson-nano.html


# install adaftruit for pwm
sudo pip3 install --upgrade pip 
sudo apt-get install python3.8-dev
sudo pip3 install adafruit-circuitpython-servokit

# find the i2c servo driver
sudo i2cdetect -y -r 1



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
