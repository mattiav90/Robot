# update
sudo apt-get update

# install opencv
sudo apt-get install python3-opencv
sudo apt-get remove python3-opencv

# install code-oss (editor)
sudo apt-get install curl
curl -L https://github.com/toolboc/vscode/releases/download/1.32.3/code-oss_1.32.3-arm64.deb -o code-oss_1.32.3-arm64.deb
sudo dpkg -i code-oss_1.32.3-arm64.deb

# setup github
cd ~/Desktop
git clone https://github.com/mattiav90/Robot.git
echo "you have to set up a ssh key manually for this"

# installing adfruit for pwm
cd ~
sudo apt-get install python3-pip
sudo apt install -y python3 git python3-pip
sudo update-alternatives --install /usr/bin/python python $(which python2) 1
sudo update-alternatives --install /usr/bin/python python $(which python3) 2
sudo update-alternatives --config python
# pick python3

sudo apt install -y python3.8
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
# this command lets you select which python to use in automatic (version)
sudo update-alternatives --config python3



sudo pip3 install adafruit-circuitpython-servokit