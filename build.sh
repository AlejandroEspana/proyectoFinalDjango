#!/bin/bash
set -o errexit

python inventory_system/manage.py migrate
python inventory_system/manage.py collectstatic --no-input
