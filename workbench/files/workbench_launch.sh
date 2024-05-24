#!/bin/bash

# title:        workbench_launch.sh
# description:  This script launches workbench jobs and is run by Slurm's srun
#               command. An interactive shell on the node is launched and 
#               relevant job details are printed out to the command line at
#               the beginning of execution. 
#author:        Christine Harvey (ceharvey@mitre.org)
#date:          18 January 2022
#version:       0.1    
# usage: workbench_launc [ options ] 
# -l login_node, login node name
# -g gpu, number of GPUs requested
# -c container_name, name of the container
# -b bind_details, container bind details
# -j, launch a jupyter notebook
# -a, specify jupyter arguements (in quotes)
# -p, port number for VS debug or Jupyter
# -v, print VS Code Debuggin instructions.
#==============================================================================



cat << EOF
 __          __        _    _                     _     
 \ \        / /       | |  | |                   | |    
  \ \  /\  / /__  _ __| | _| |__   ___ _ __   ___| |__  
   \ \/  \/ / _ \| '__| |/ / '_ \ / _ \ '_ \ / __| '_ \ 
    \  /\  / (_) | |  |   <| |_) |  __/ | | | (__| | | |
     \/  \/ \___/|_|  |_|\_\_.__/ \___|_| |_|\___|_| |_|
                                                        
EOF

# Color printing
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Options for running
while getopts l:g:c:b:ja:p:v option
do
    case "${option}"
        in
        l)LOGIN=${OPTARG};;
        g)GPUS=${OPTARG};;
        c)CONTAINER=${OPTARG};;
        b)BIND=${OPTARG};;
        j)JUPYTER=TRUE;;
        a)JUPYTER_ARGS=${OPTARG};;
        p)PORT=${OPTARG};;
        v)VS_DEBUG=TRUE;;
    esac
done

# Add to the Welcome statement
printf "
*****
Welcome to the WORKBENCH!
Your job is running on $(hostname -s)
"
if [ $GPUS -gt 0 ]
then
    printf "You have $GPUS GPU(s) reserved:\n"
    nvidia-smi -L
fi
printf "*****\n"

VS_INSTRUCTIONS="
    Visual Studio Debug Instructions
    --------------------------------------------------------------
    To access the WORKBENCH reservation with Visual Studio Debug,
    Take the following additional steps. 
    1. From a separate terminal on your local machine, connect to
        the host with port forwarding
        ${RED}ssh -t -t $USER@$LOGIN -L $PORT:localhost:$PORT ssh $(hostname -s) -L $PORT:localhost:$PORT${NC}
    2. Run the python script from workbench terminal:
        ${RED}python -m debugpy --wait-for-client --listen $PORT <filename>.py${NC}
    3. Take the following VS Code Debug Config and run it to attach to the script:
        {
            'name': 'Workbench Debug',
            'type': 'python',
            'request': 'attach',
            'host': 'localhost',
            'port': $PORT,
            'pathMappings': [
                {
                    'localRoot': '\${workspaceFolder}',
                    'remoteRoot': '.'
                }
            ]
        }

"

# Print out debug instructions if needed
if [ $VS_DEBUG ]
then
    printf "$VS_INSTRUCTIONS"
fi

JUPYTER_INSTRUCTIONS="
        Jupyter Lab Instructions
        --------------------------------------------------------------
        1. WAIT for Jupyter to launch in this window.
        2. Connect to your notebook by running the following on your LOCAL machine:
            ${RED}ssh -t -t $USER@$LOGIN -L $PORT:localhost:$PORT ssh $(hostname -s) -L $PORT:localhost:$PORT${NC}
        3. Go to a local browser and open ${RED}http://localhost:$PORT/lab${NC}
        4. Use Control-C followed by 'y' or the browser tool to kill the notebook.

        Refer to the documentation for troubleshooting support: 
            https://gitlab.mitre.org/hpc/hpc-examples/-/tree/master/jupyter_lab

"

# Print proper output for the statement
# Launch a Container or Environment
if [ -z "$CONTAINER" ]
then
    # NATIVE
    if [ $JUPYTER ]
    then
        # Jupyter notebook
        printf "$JUPYTER_INSTRUCTIONS"
        jupyter lab $JUPYTER_ARGS --no-browser --port=$PORT 
    else 
        # BASH Shell
        echo "Type 'exit' to leave the workbench."
        # Launch a bash prompt and printing present working Directory
        # Additional if statement added to handle RDP session VTE errors
        bash --init-file <(echo ". ~/.bash_profile; if ! type -t _vte_prompt_command; then unset PROMPT_COMMAND; fi; printf 'Present Working Directory: '; pwd; echo "";")
    fi
else
    # CONTAINER
    if [ $JUPYTER ]
    then
        # Jupyter notebook
        printf "$JUPYTER_INSTRUCTIONS"
        apptainer exec --nv $BIND $CONTAINER jupyter lab $JUPYTER_ARGS --no-browser --port=$PORT
    else
        echo "Running container: $CONTAINER"
        echo "Type 'exit' to leave the workbench."
        apptainer shell --nv $BIND $CONTAINER
    fi
fi
