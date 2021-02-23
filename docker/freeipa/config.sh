#! /bin/bash

# Bash config script for test IPA cluster

# Define domain
Domain_Name="test.local"

# Define cluster master node hostnames and IP adresses
MASTER_1="ipa-master-1.${Domain_Name}"
MASTER_1_IP="172.18.1.11"
MASTER_2="ipa-master-2.${Domain_Name}"
MASTER_2_IP="172.18.1.12"

# Define cluster satellite node hostnames and IP addresses
SAT_1="ipa-satellite-1.${Domain_Name}"
SAT_1_IP="172.18.1.21"
SAT_2="ipa-satellite-2.${Domain_Name}"
SAT_2_IP="172.18.1.22"

# Define cluster test client node hostnames and IP addresses
CLIENT_1="client-1.${Domain_Name}"
CLIENT_1_IP="172.18.1.31"
CLIENT_2="client-2.${Domain_Name}"
CLIENT_2_IP="172.18.1.32"

# Set up array


# Update hosts file
echo -e "\n#IPA Cluster\n\
${MASTER_1_IP}\t${MASTER_1}\n\
${MASTER_2_IP}\t${MASTER_2}\n\
${SAT_1_IP}\t${SAT_1}\n\
${SAT_2_IP}\t${SAT_2}" >> /etc/hosts
