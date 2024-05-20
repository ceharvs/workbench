#!/bin/python3

import argparse
import os
import subprocess
import random
import socket

def check_availability(slurm_requirements):
    """Check Expected Start Time with --test-only function"""
    srun_string = "srun %s --test-only hostname"%(slurm_requirements)
    estimated_start = subprocess.run(srun_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("\nEstimated Start Time: \033[31m%s\033[0m" % estimated_start.stderr.decode().strip().split(' ')[6])
    print("If the job takes longer than 1-2 minutes to start, check \033[96mcspan.mitre.org\033[0m and\n\033[96msqueue\033[0m for resource availability. If utilization is at capacity, the\ninteractive option may be unavailable.\n")

def is_port_in_use(port):
    """Check if ports are in use for Jupyter Notebooks"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_open_port():
    """Find an open port leveraging Numpy's Random Number Generator
    The search field is a set of 20 randomly generated numbers.
    This can be increased if necessary. """
    used_port = True
    while used_port:
        port = random.randint(8008,8099)
        used_port = is_port_in_use(port)
    return port

def parser():
    """Command Line Arguments"""
    parser = argparse.ArgumentParser(description="""Launch an interactive job via Slurm on the HPC cluster.
    In addition to the commands listed, any sbatch arguments will also work on the command line. Workbench will
    only launch jobs on a single node.
    For more information on sbatch commands: https://slurm.schedmd.com/sbatch.html""")
    parser.add_argument("-g", "--gpus", dest="gpu_count", default=1, type=int,
                choices=[0,1,2,3,4],
                help="Number of GPUs requested.")
    parser.add_argument("-k", "--kind", dest="gpu_kind", default=None, type=str,
                choices=['k80','m40','p100','v100','a100', 'a40'],
                help="Type of GPU, use scontrol show nodes to review which gpu types are available.")
    parser.add_argument("-c", "--cpus", dest="cpu_count", default=5, type=int,
                help="Number of CPUs.")
    parser.add_argument("-t", "--time", dest="wallclock",default=4, type=int,
                help="Expected reservation duration in hours.")
    parser.add_argument("-m", "--mem", dest="memory", default="50G", type=str,
                help="Expected memory required for the job. Specify units with K|M|G immediately after numerical value. Default is M.")
    parser.add_argument("-p", "--partition", dest="partition", default="batch,short_jobs", type=str,
                help="Partition to run the job on.")
    parser.add_argument("-A", "--account", dest="account", default=None, type=str,
                help="Associated project for accounting.")
    parser.add_argument("--vs_debug", dest="vs_debug", default=False, action="store_true",
                help="Launch an interactive VS Code Debug Session.")
    parser.add_argument("--jupyter", dest="jupyter", default=False, action="store_true",
                help="Launch a Jupyter Notebook instance.")
    parser.add_argument("--jupyter_args", dest="jupyter_args", default=None, type=str,
                help="Additional arguments for Jupyter. Provide in quotes. Do NOT include port or --no-browser.")
    parser.add_argument("--container", dest="container_name", default=None, type=str,
                help="Launch a specific apptainer container. Provide the .simg file name.")
    parser.add_argument("--bind", dest="bind", default=None, type=str,
                help="Input for apptainer bind command.")
    args, unknown_args = parser.parse_known_args()
    return args, unknown_args


def main():
    """Execute the srun command"""
    # Read in Command Line Arguments
    args, unknown_args = parser()

    # Build the String
    account = "--account=%s"%(args.account) if args.account else ""
    partition = "--partition=%s"%(args.partition) if args.partition else ""
    gpu_request = "%s:%d"%(args.gpu_kind, args.gpu_count) if args.gpu_kind else "%d"%(args.gpu_count)
    sbatch_options = ' '.join(unknown_args)
    login_node = os.environ['HOSTNAME'].split('.')[0]

    # Build Requirements - must begin with -v for proper parsing later
    slurm_requirements = " -N1 --qos=high --gpus-per-node=%s -c%d --mem=%s -t%d:00:00 -J'Workbench Job' %s %s %s"%(gpu_request,
        args.cpu_count, args.memory, args.wallclock, account, partition, sbatch_options)

    # Print details
    confirmation_print = """\nPlease wait for your allocation to be created. You have requested:
        -GPUs: %s
        -CPUs: %d
        -Memory: %s
        -Time: %d Hours"""%(gpu_request,
        args.cpu_count, args.memory, args.wallclock)
    print(confirmation_print)
    if args.account:
        print("        -Account: %s"%args.account)

    # Check start time
    check_availability(slurm_requirements)

    # Configure arguments for launch
    arg_string = " -g %d -l %s "%(args.gpu_count, login_node)
    arg_string += ' -c %s '%(args.container_name) if args.container_name else ''
    arg_string += ' -b --bind=%s '%(args.bind) if args.bind else ''
    arg_string += ' -j ' if args.jupyter else ''
    arg_string += ' -a "%s"'%(args.jupyter_args) if args.jupyter_args else ''
    arg_string += ' -p %d'%(find_open_port()) if (args.jupyter or args.vs_debug) else ''
    arg_string += ' -v ' if args.vs_debug else ''

    # Launch the workbench script
    srun_string = "srun %s --pty /usr/bin/workbench_launch.sh %s "%(slurm_requirements, arg_string)
    subprocess.run(srun_string, shell=True)

    print("\nThe interactive session has ended.\n")


if __name__ == '__main__':
    main()
