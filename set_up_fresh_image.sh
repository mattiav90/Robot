# update
sudo apt-get update

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


# install adaftruit for pwm
sudo pip3 install --upgrade pip
sudo apt-get install python3.8-dev
sudo pip3 install adafruit-circuitpython-servokit

# find the i2c servo driver
sudo i2cdetect -y -r 1
