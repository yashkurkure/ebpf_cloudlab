#!/bin/bash

make

python3 /local/repository/ebpf_service/client.py $$

mpirun -np 4 ./avg

python3 /local/repository/ebpf_service/client.py $$