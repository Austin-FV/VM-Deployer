# Azure and GCP VM Deployer
> Austin Varghese

## Python script that automates creation and deployment of VMs on Azure and GCP

### automate.py will:
 - read .conf and create VM's described
 - check if enough info is given
 - print out command before execution (prints out cli command used before using, or the sdk used but unlikely)
 - print out information that command returns 
 - write to a file: VMcreation_date.txt that will contain date, system admin name, and then details of VM created
 - copy the used .conf files to azure_date.conf and gcp_date.conf respectively to save as history

### How to run the program:
 - Need to be authorized and logged into Azure CLI and GCP CLI. The GCP projects that are used must have the compute API enabled.
 - Must have files called 'Azure.conf' and 'GCP.conf' that follow a set format listed below.
 - To open ports for the VM's, the format within the config files must be 'ports = 80,443' / 'ports = 443,80', no space in between selected ports or just a single port
 - Finally, run the python script automation.py 
 
### CONFIG FILE FORMAT 
 Azure.conf
 - Azure.conf mandatory fields: ['purpose', 'os', 'name', 'resource-group', 'team', 'image', 'location', 'admin-username']
 - Azure.conf additonal fields available: ['admin-password', 'size', 'ports', 'project']
 - NOTE: admin-password is only for window vm's and project is for documentation.

 GCP.conf
 - ** NAME must be first value ! **
 - GCP.conf mandatory fields: ['name', 'project', 'team', 'purpose', 'os', 'image', 'imageproject', 'zone']
 - GCP.conf additonal fields: ['ports', 'custom-cpu', 'custom-memory', 'machine-type', 'threads-per-core', 'project-id']
 - NOTE: project-id is for specifying a different project outside of the set project. cannot use machine-type with custom-memory and custom-cpu
 
 > To open ports, format must be "ports = 80,443" or just "ports = 80". no spaces between anything.

### Normal Behaviour:
 - The script may take sometime based upon how many VM's are created.
 - If unknown variables exist in config files, it will ignore them
 - for every VM created, the CLI command will be printed with differing messages in the terminal based on success or failure.
 - Once the script is completed: 
 - - A new file will be generated: VMcreation_<date stamp>.txt that will contain date, system admin name, and then details of all VM's created.
 - - 2 config files that are copies of the used azure and gcp config files.
 - - These files are found in 2 folders that are created, one for storing a log of config files, the other for storing a log of VM creation files
 - The script only has as much authorization as the CLI for Azure and GCP, and any errors will be found if attempting something impossible
 - The script will ignore fields in the config files if it is not one of the mandatory/additonal fields listed.

### Limitations:
 - Doesn't create resource group for you first, it must exist first.
 - For GCP VM's, each section within the GCP.conf must start with the name of the VM to be created 
 - Error checking is done through the CLI as it is very hard to catch all the errors within the config file myself.
 - TO OPEN PORTS: The format within the config files must be 'ports = 80,443' / 'ports = 443,80', no space in between selected ports or just a single port
 - For GCP, I am only able to open ports 80 and 443 (this is not really a limitation of my program rather a limitation of GCP)
 - In Azure, if you create too many VM's and exceed the Usage and Quota limit for a region on your account it will fail to create the VM's.
 - If your GCP account doesnt have access to create Window Servers then it will not let you (this costs extra and is not in the free tier).
 - ANYTHING THAT AZURE AND GCP CLI DOESNT ALLOW I DONT ALLOW (such as machine type with custom cpu/memory) 

** Uploaded example Azure.conf and GCP.conf to show formatting **