#!/bin/bash

set -o errexit
cd /home/telescope/EGR-385-Telescope-Mount

function checkInternet {
    curl -s --head  --request GET https://www.google.com | grep "200" > /dev/null
}

# If we don't have internet, that is okay, just don't try to pull anything.
if checkInternet; do
  git pull
done

sudo python3 -m telescope

exit 0