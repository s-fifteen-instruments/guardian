#!/bin/sh
envsubst < simulate_keygen.py.conf.example > simulate_keygen.py.conf
python3 simulate_keygen.py --config simulate_keygen.py.conf
