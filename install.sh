#!/bin/bash
sudo apt update
sudo apt install -y python3-pip git
git clone https://github.com/Mac-Coleman/EGR-385-Telescope-Mount.git
cd EGR-385-Telescope-Mount
git config pull.rebase false
sudo -H python3 -m pip install -e .
sudo cp -v ./bin/telescope.service /lib/systemd/system/
sudo systemctl enable telescope.service
cd telescope
python3 setup_database.py
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "dtoverlay=pwm-2chan" | sudo tee -a /boot/config.txt
echo "dtparam=i2c_arm_baudrate=400000" | sudo tee -a /boot/config.txt
echo "dtoverlay=i2c-gpio,bus=4,i2c_gpio_sda=17,i2c_gpio_scl=27" | sudo tee -a /boot/config.txt
sudo reboot now