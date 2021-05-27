# This script will install Watch and Set Fire and any required prerequisites.
cd ~
echo -e ''
echo -e '\033[32mWatch and Set Fire [Installation Script] \033[0m'
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e ''
echo -e '\033[93mUpdating package repositories... \033[0m'
sudo apt update

echo ''
echo -e '\033[93mInstalling prerequisites... \033[0m'
sudo apt install -y git python3 python3-pip
sudo pip3 install --upgrade six google-cloud-storage firebase firebase_admin watchdog --force

echo '\033[93mProvisioning logs... \033[0m'
sudo mkdir -p /home/pi/logs
sudo chmod +rw /home/pi/logs
sudo sed -i '\|^tmpfs /home/pi/logs|d' /etc/fstab
sudo sed -i '$ a tmpfs /home/pi/logs tmpfs defaults,noatime,nosuid,size=16m 0 0' /etc/fstab
sudo mount -a

echo ''
echo -e '\033[93mInstalling "Watch and Set Fire"... \033[0m'
cd ~
sudo rm -Rf ~/watchandsetfire
sudo git clone https://github.com/eat-sleep-code/watchandsetfire
sudo chown -R $USER:$USER watchandsetfire
cd watchandsetfire
sudo chmod +x watchandsetfire.py

echo ''
echo -e '\033[93mCreating Service... \033[0m'
sudo mv watchandsetfire.service /etc/systemd/system/watchandsetfire.service
sudo chown root:root /etc/systemd/system/watchandsetfire.service
sudo chmod +x *.sh 
echo 'Please see the README file for more information on configuring the service.'

cd ~
echo ''
echo -e '\033[93mSetting up aliases... \033[0m'
sudo touch ~/.bash_aliases
sudo sed -i '/\b\(function watchandsetfire\)\b/d' ~/.bash_aliases
sudo sed -i '$ a function watchandsetfire { sudo python3 ~/watchandsetfire/watchandsetfire.py "$@"; }' ~/.bash_aliases
echo -e 'You may use \e[1mwatchandsetfire <options>\e[0m to launch the program.'
echo ''
echo 'To use this program, you will need to update the firebase-key.json file.'
echo 'Please see the README file for more information.'
echo ''
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e '\033[32mInstallation completed. \033[0m'
echo ''
bash

