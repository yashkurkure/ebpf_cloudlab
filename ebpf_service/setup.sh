# Notes
# View logs: journalctl -u ebpf.service


sudo cp /local/repository/ebpf_service/ebpf.service /etc/systemd/system/ebpf.service
sudo systemctl enable ebpf.service
sudo systemctl start ebpf.service