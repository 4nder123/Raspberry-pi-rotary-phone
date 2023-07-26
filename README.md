# INSTALLATION
- Install Bluealsa
```
sudo apt install ofono git automake build-essential libtool pkg-config libasound2-dev libbluetooth-dev libdbus-1-dev libglib2.0-dev libsbc-dev
git clone https://github.com/Arkq/bluez-alsa
cd bluez-alsa
autoreconf --install
mkdir build && cd build
../configure --enable-ofono --enable-debug --enable-aplay
make
sudo make install
```
```
pip install pexpect
```
- Uninstall Pulseaudio
```
sudo apt-get remove pulseaudio
```
