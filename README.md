# advancedpwmdriver
Control software for the Industrial Board built for Barnwood Model Railway Club - www.barnwoodmodelrailwayclub.org.uk/

# setting up raspberry pi to run advancedpwmdriver software

#1] Install all the required python libraries and pygame for python3 (some may already be present on the Pi)
sudo apt-get install git build-essential python-dev python3-dev python3-setuptools python3-pip python3-smbus
sudo pip3 install pygame

#2] Install the Adafruit PCA9685 library, then build for both python2 and python3
cd ~
git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git
cd Adafruit_Python_PCA9685
sudo python setup.py install
sudo python3 setup.py install

#3] Install the Adafruit ADS1x15 library, then build for both python2 and python3
cd ~
git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git
cd Adafruit_Python_ADS1x15
sudo python setup.py install
sudo python3 setup.py install

#4] to run the python3 versions
python3 curses-main.py bmrcdemoautosequence.cfg
python3 pygame-main.py bmrcdemoautosequence.cfg
python3 proximity_test.py
