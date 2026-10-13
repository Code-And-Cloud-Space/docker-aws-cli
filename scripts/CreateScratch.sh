# Script For Creating Scratch Org
#! /bin/bash

SCRATCH_ORG_ALIAS=""               #your scratch org name
PACKAGENAME="Charge On"                       #package name
choice=""
RED='\033[0;31m'
NC='\033[0m'
Black='\033[0;30m'           
Green='\033[0;32m'    
Yellow='\033[0;33m'    
Blue='\033[0;34m'    
Purple='\033[0;35m'    
Cyan='\033[0;36m'    
White='\033[0;37m'
 
read -p "Want to Delete Scratch Org (y/n) " choice
if [ "$choice" == "y" ];
  then
    echo "Enter Scratch org Name"
    read SCRATCH_ORG_ALIAS
    echo "Deleting scratch ORG..."
    sf org:delete:scratch -o $SCRATCH_ORG_ALIAS
  fi
 
read -p "Want to Create Scratch Org (y/n) " choice
if [ "$choice" == "y" ];
  then
    echo "Enter Scratch org Name"
    read SCRATCH_ORG_ALIAS
    echo "Creating scratch ORG..."
    sf org:create:scratch -f config/project-scratch-def.json -a $SCRATCH_ORG_ALIAS -d -y 30
  fi

echo "Want to Push Source to${Green} ${SCRATCH_ORG_ALIAS} ${NC}Org (y/n)"
read choice
if [ "$choice" == "y" ];
  then
    echo "${Green}Pushing changes to scratch org...${NC}"
    sf project:deploy:start
  fi
read -p "Press enter to continue"