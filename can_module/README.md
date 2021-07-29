# Afron-Canbus
A Linux micro process part of the Afron application


1. Install seed CAN hat driver
  https://wiki.seeedstudio.com/2-Channel-CAN-BUS-FD-Shield-for-Raspberry-Pi/



2. Add the following to /etc/profile (at the end of the file)
  sudo ip link set can0 up type can bitrate 1000000   dbitrate 8000000 restart-ms 1000 berr-repo$
  sudo ip link set can1 up type can bitrate 1000000   dbitrate 8000000 restart-ms 1000 berr-repo$

  sudo ifconfig can0 txqueuelen 65536
  sudo ifconfig can1 txqueuelen 65536

3. copy can.conf to /etc

4. install python modules 
  > common (see README.MD file at the common directory)

5. install pigpio-pwm module
   - Install services
      > sudo apt install libpigpiod-if-dev pigpiod
      > sudo systemctl start pigpiod
      > sudo systemctl enable pigpiod
   - Install the python package
      > git clone https://github.com/rotshtein/pigpio-pwm.git
      > cd pigpio-pwm
      > sudo python setup.py install

6. Install the canbus package - from the canbus directory
    > sudo pip install -e .


Fast boot:
1. Disable components at boot:

  # setting for faster boot
  disable_splash=1
  dtoverlay=disable-bt
  dtoverlay=disable-wifi
  boot_delay=0


  [all]
  # canbus hat
  dtoverlay=2xMCP2517FD,oscillator=8000000
  dtoverlay=2xMCP2518FD-spi0,oscillator=8000000
  hdmi_enable_4kp60=1


2. Disable systemd services
  wpa_supplicant.service
  ifupdown-pre.service
  hciuart 
  raspi-config
  avahi-daemon
  
3. Add the hlc.service to /etc/systemd/system directory and enable the service