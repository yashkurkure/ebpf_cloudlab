sudo systemctl stop ebpf.service
sudo systemctl disable ebpf.service
sudo rm /etc/systemd/system/ebpf.service
sudo systemctl daemon-reload