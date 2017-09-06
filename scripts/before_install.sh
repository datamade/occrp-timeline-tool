#!/bin/bash

# Cause entire deployment to fail if supervisor fails
set -euo pipefail

# Make project directory if it doesn't exist. This is mainly to ensure that these scripts work on a bare server
rm -Rf /home/datamade/occrp-timeline-tool
mkdir -p /home/datamade/occrp-timeline-tool

# Decrypt files encrypted with blackbox
cd /opt/codedeploy-agent/deployment-root/$DEPLOYMENT_GROUP_ID/$DEPLOYMENT_ID/deployment-archive/ && chown -R datamade.datamade . && sudo -H -u datamade blackbox_postdeploy