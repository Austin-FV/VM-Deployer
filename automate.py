#!/usr/bin/env python3
# Austin Varghese
# 1098759
# CIS*4010
# Assignment 3 - Azure and GCP VMS 

#
#  Libraries and Modules
#
import configparser
import os
import json
from datetime import datetime
import getpass

az_conf_file = "Azure.conf"
gcp_conf_file = "GCP.conf"

# reading in the config files
az_config = configparser.ConfigParser()
az_config.read(az_conf_file)

gcp_config = configparser.ConfigParser()
gcp_config.read(gcp_conf_file)

# get current time - to be used for filenames
now = datetime.now()
# date stamp format: "yyyy-mm-dd:hh:mm:ss"
datestamp = now.strftime("%Y-%m-%d:%H:%M:%S")
# print(datestamp)

# colons do not format nicely on windows so replace : with ;
file_datestamp = datestamp.replace(":","'")

# need to get system admin username

sys_admin_name = getpass.getuser()
# print(sys_admin_name)

# os.getlogin()
# os.getenv('USERNAME')
# os.getegid()
# print(os.getegid())

print("VM Deployment Automation Script\n")

# make folder to store vm creation files
# if not os.path.exists("vmlog"):
os.makedirs("vmlog", exist_ok=True)

# # make file to store all created vm information
f = open("vmlog/VMcreation_"+file_datestamp+".txt","w+")

f.write("VM Creation\n")
f.write(datestamp+"\n")
f.write("System Admin: "+sys_admin_name+"\n\n")

# make folder to store config files
# if not os.path.exists("configlog"):
os.makedirs("configlog", exist_ok=True)
# # copy config files to new files
# # open both files
with open(az_conf_file,'r') as firstfile, open('configlog/azure_'+file_datestamp+'.conf','w') as secondfile:
    # read content from first file
    for line in firstfile:
        # write content to second file
        secondfile.write(line)

with open(gcp_conf_file,'r') as firstfile, open('configlog/gcp_'+file_datestamp+'.conf','w') as secondfile:
    # read content from first file
    for line in firstfile:
        # write content to second file
        secondfile.write(line)

# required azure options in Azure.conf
az_req_opts = ['purpose', 'os', 'name', 'resource-group', 'team', 'image', 'location', 'admin-username']

# required gcp options in GCP.conf
gcp_req_opts = ['name', 'project', 'team', 'purpose', 'os', 'image', 'imageproject', 'zone']

# PARSE CONFIG FILES and create each vm listed
output = ""
# AZURE
f.write("Azure Virtual Machine's:")
for section in az_config.sections():

    # will append necessary information to complete this command
    az_cli = "az vm create"

    # values to store
    purpose = ""
    vm_os = ""
    team = ""
    resource_group = ""
    vm_name = ""
    image = ""
    location = ""
    admin_username = ""

    size = ""
    ports = ""
    # IF CREATING WINDOWS SERVER, NEED ADMIN PASSWORD
    admin_password = ""
    project = ""

    # ADDITIONAL INFO FROM 'az vm create'
    macAddress = ""
    powerState = ""
    privateIP = ""
    publicIP = ""

    print("Creating VM:", section)

    # print ('  Options:', az_config.options(section))
    # check if options contain required information before going to next step
    check = all(item in az_config.options(section) for item in az_req_opts)
    if not check:
        print("ERROR: Required parameters not found in",section,"of",az_conf_file)
        continue

    # go through each item in config file 
    for name, value in az_config.items(section):

        # print(name, value)

        if name == "purpose":
            purpose = value

        if name == "os":
            vm_os = value

        if name == "name":
            vm_name = value
            az_cli+=" --name " + vm_name

        if name == "resource-group":
            resource_group = value
            az_cli+=" --resource-group " + resource_group

        if name == "team":
            team = value

        if name == "image":
            image = value
            az_cli+=" --image " + image

        if name == "location":
            location = value
            az_cli+=" --location " + location

        if name == "admin-username":
            admin_username = value
            az_cli+=" --admin-username " + admin_username  

        if name == "size":
            size = value
            az_cli+=" --size " + size

        # add error checking, 12-123 char length, 3 of 1 lowercase, 1 uppercase, 1 number, 1 special char
        if name == "admin-password":
            admin_password = value
            az_cli+=" --admin-password " + admin_password
        
        if name == "ports":
            ports = value
            # az_cli+=" --size " + size

    # final command to be called in cli:
    # generate ssh keys if not there 
    # would run in background to make script faster, however need output to be shown "--no-wait"
    # no warnings: '--only-show-errors' no errors '2>nul'
    az_cli += " --generate-ssh-keys --only-show-errors"
    print(az_cli)

    # # run cli and save output
    output = os.popen(az_cli).read()
    # print("output:",output)

    # # changes json string to json (dict in python)
    try:
        json_output = json.loads(output)
        
        macAddress = json_output['macAddress']
        powerState = json_output['powerState']
        privateIP = json_output['privateIpAddress']
        publicIP = json_output['publicIpAddress']
        print("\nSuccessfully created VM ["+section+"]")
        print("\tName:",vm_name)
        print('\tLocation:',location)
        print('\tResource Group:', resource_group)
        print('\tImage:',image)
        print('\tAdmin Username:',admin_username)
        print('\tMAC Address:', macAddress)
        print('\tVM State:', powerState)
        print('\tPrivate IP Address:', privateIP)
        print('\tPublic IP Address:', publicIP)
        print("")
        # print("\tsuccessfully parsed 'az vm create' output")
    except ValueError as e:
        json_output = {}
        print("\nERROR: unable to create VM", section+"\n")
        powerState = "Unable to create"
        # print("\tunable to parse 'az vm create' output")
        # print("\tactual output:\n",output)
    # json_output = json.loads(output)
    # print (json_output)

    # ports can be added at the same time, if not at the same time must add priority (--priority 100)
    # in my case they will be at the same time, as long as the numbers are comma seperated it should work
    if ports != "" and json_output != {}:
        az_port_cli = "az vm open-port --name " + vm_name + " --resource-group " + resource_group + " --port "
        az_port_cli+=ports
        print(az_port_cli)

        # run cli and save output
        output = os.popen(az_port_cli).read()
        # print(output)

        # changes json string to json (dict in python)
        try:
            json_output = json.loads(output)
            print("\nSuccessfully opened ports:",ports + " for",vm_name,"\n")
            # print(json_output)

            # print("\tsuccessfully parsed 'az vm open-port' output")
        except ValueError as e:
            json_output = {}
            print("\nERROR: unable to open ports for", vm_name+"\n")

            # print("\tunable to parse 'az vm open-port' output")
            # print("\tactual output:\n",output)
        # json_output = json.loads(output)
        # print (json_output)

    # write required information to file
    f.write("\n\n["+section+"]")
    f.write("\nVM Name: " + vm_name)
    f.write("\nProject: " + project)
    f.write("\nPurpose: " + purpose)
    f.write("\nTeam: " + team)
    f.write("\nOperating System: " + vm_os)
    f.write("\nVM Status: " + powerState)
    f.write("\nVM Information: ")
    f.write('\n\tResource Group: ' + resource_group)
    f.write('\n\tImage: ' + image)
    f.write('\n\tAdmin Username: ' + admin_username)
    f.write('\n\tLocation: ' + location)
    f.write('\n\tMAC Address: ' + macAddress)
    f.write('\n\tPrivate IP Address: ' + privateIP)
    f.write('\n\tPublic IP Address: ' + publicIP)

print()

# GCP
f.write("\n\nGCP Virtual Machine's:")

for section in gcp_config.sections():
    print("Creating VM: ", section)

    # will append necessary information to complete this command
    gcp_cli = "gcloud compute instances create"

    # values to store for file
    purpose = ""
    vm_os = ""
    team = ""
    resource_group = ""
    vm_name = ""
    project = ""
    image = ""
    imageproject = ""
    zone = ""

    size = ""
    ports = ""
    custom_cpu = ""
    custom_memory = ""
    threads_per_core = ""
    machine_type = ""

    # if you would want to set project that is not the configured project of the cli
    project_id = ""
    
    # additional info from creation
    powerState = ""
    privateIP = ""
    publicIP = ""

    # print ('  Options:', gcp_config.options(section))

    check = all(item in gcp_config.options(section) for item in gcp_req_opts)
    if not check:
        print("ERROR: Required parameters not found in",section,"of",gcp_conf_file)
        continue

    # would like to find a way so the order doesnt matter with the name, however it isnt efficient and will likely make this a limitation
    # print(gcp_config.items(section))

    # TO ADD PORTS: 
    # --tags=http-server,https-server

    # go through each item in config file 
    for name, value in gcp_config.items(section):
    #     print(name, value)
        # NAME HAS TO BE FIRST ADDED WITH GCLOUD CLI FORMAT
        if name == "name":
            vm_name = value
            gcp_cli+=" "+value

        elif name == "project":
            project = value

        elif name == "team":
            team = value

        elif name == "purpose":
            purpose = value

        elif name == "os":
            vm_os = value

        elif name == "image":
            image = value
            gcp_cli+=" --image="+image
            
        # public images
        elif name == "imageproject":
            imageproject = value
            gcp_cli+=" --image-project="+imageproject

        elif name == "zone":
            zone = value
            gcp_cli+=" --zone="+zone

        elif name == "size":
            size = value
            gcp_cli+=" --size="+size

        elif name == "custom-cpu":
            custom_cpu = value
            gcp_cli+=" --custom-cpu="+custom_cpu

        elif name == "custom-memory":
            custom_memory = value
            gcp_cli+=" --custom-memory="+custom_memory

        elif name == "threads-per-core":
            threads_per_core = value
            gcp_cli+=" --threads-per-core="+threads_per_core

        elif name == "ports":
            # --tags=http-server,https-server (80, 443)
            ports = value

            # input must be '80,443' (no spaces)
            list_ports = ports.split(",")
            
            tags = ""
            port80 = 0
            port443 = 0

            if "80" in list_ports:
                port80 = 1

            if "443" in list_ports:
                port443 = 1

            if port80 + port443 == 2:
                # print("both")
                tags="http-server,https-server"
            else:
                if port80 == 1:
                    # print("80")
                    tags="http-server"
                elif port443 == 1:
                    # print("443")
                    tags="https-server"
                else:
                    tags=ports

            gcp_cli+=" --tags="+tags

        elif name == "machine-type":
            machine_type = value
            gcp_cli+=" --machine-type="+machine_type

        # if this is not here it will use the current prject from gcloud init
        elif name == "project-id":
            project_id = value
            gcp_cli+=" --project="+project_id

    # final command to be called
    # could add "--async" to run it instantly without waiting for progress, however need output
    # get the information as json to parse and print out
    gcp_cli+=" --format=json"
    print(gcp_cli)

    # # run cli and save output
    output = os.popen(gcp_cli).read()
    # print(output)

    # # changes json string to json (dict in python)
    try:
        json_output = json.loads(output)

        # macAddress = json_output['macAddress']
        powerState = json_output[0]['status']
        privateIP = json_output[0]['networkInterfaces'][0]['networkIP']
        publicIP = json_output[0]['networkInterfaces'][0]['accessConfigs'][0]['natIP']
        
        print("\nSuccessfully created VM ["+section+"]")
        print("\tName:",vm_name)
        print('\tZone:',zone)
        print('\tImage Project:', imageproject)
        print('\tImage:',image)
        # print('\tAdmin Username:',admin_username)
        # print('\tMAC Address:', macAddress)
        print('\tVM State:', powerState)
        print('\tInternal IP Address:', privateIP)
        print('\tExternal IP Address:', publicIP)
        print("")
        # print("\tsuccessfully parsed 'az vm create' output")
    except ValueError as e:
        json_output = {}
        print("\nERROR: unable to create VM", section+"\n")
        powerState = "Unable to create"
        # print("\tunable to parse 'gcloud compute instances create' output")
        # print("\tactual output:\n",output)



    # write required information to file
    f.write("\n\n["+section+"]")
    f.write("\nVM Name: " + vm_name)
    f.write("\nProject: " + project)
    f.write("\nPurpose: " + purpose)
    f.write("\nTeam: " + team)
    f.write("\nOperating System: " + vm_os)
    f.write("\nVM Status: " + powerState)
    f.write("\nVM Information: ")
    f.write('\n\tImage Project: ' + imageproject)
    f.write('\n\tImage: ' + image)
    # f.write('\n\tAdmin Username: ' + admin_username)
    f.write('\n\tZone: ' + zone)
    # f.write('\n\tMAC Address: ' + macAddress)
    f.write('\n\tInternal IP Address: ' + privateIP)
    f.write('\n\tExternal IP Address: ' + publicIP)

# close file after going through each section of both config files
f.close()