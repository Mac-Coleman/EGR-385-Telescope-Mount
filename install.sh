sudo apt update
sudo apt install -y python3-pip git
git clone https://github.com/Mac-Coleman/EGR-385-Telescope-Mount.git
cd EGR-385-Telescope-Mount
git config pull.rebase false
sudo -H python3 -m pip install -e .
sudo cp -v ./bin/telescope.service /lib/systemd/system/
sudo systemctl enable telescope.service
sudo reboot now