# INSTALLATION
- Install Bluealsa
```
git clone https://github.com/Arkq/bluez-alsa
cd bluez-alsa
autoreconf --install
mkdir build && cd build
../configure --enable-ofono --enable-debug --enable-aplay
make
sudo make install
```
- Uninstall Pulseaudio
```
sudo apt-get remove pulseaudio
```
