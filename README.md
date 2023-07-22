# INSTALLATION
- Install Bluealsa
```
git clone git@github.com:raspberrypi-ui/bluealsa.git && cd bluealsa/
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
