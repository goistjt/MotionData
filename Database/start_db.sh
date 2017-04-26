#!/bin/bash
docker run -d -v data:/var/lib/mysql db ./setup.sh
