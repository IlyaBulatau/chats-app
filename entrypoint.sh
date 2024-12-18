#!/bin/bash

export PYTHONPATH=`pwd`
python3 cli/migrate.py
uvicorn main:app --host 0.0.0.0 --port 8000 --log-config ./log_config.yaml --log-level info --proxy-headers --forwarded-allow-ips=*