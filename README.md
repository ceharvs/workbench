Workbench
=========

This files used in this repository cna be deployed as an Ansible role to installs the correct files for Workbench on HPC clusters.

Workbench is a simple wrapper script that supports quick and easy GPU job deployments on HPC Clusters.

Why Workbench
-------------
Users need to be able to ...
* ... launch a single large simulation
* ... launch hundreds of simulaions
* ... submit jobs and walk away

They also need...
* ... to debug
* ... to launch interactive workloads
* ... resources *now*
* ... to not learn too many new things

Slurm is a great resource for all points but the last one.  New users to Slurm that haven't worked on traditional HPC clusters aren't looking to learn the complicated Slurm syntax to launch jobs interactively.

Interactive Jobs in Slurm
-------------------------

The `srun` command can submit a job that runs right away:
```bash
$ srun hostname
gpu1.cl.cluster.local
```

It can also launch in an interactive terminal:
```bash
$ srun --pty $BASH
[user@gpu1 ~]$
```

Additional Slurm options can be added to meet user's needs:
```bash
$ srun -t60 -c5 --mem=50GB --gpus=1 --pty $BASH
[user@gpu1 ~]$
```

Why does this Fail?
-------------------

The above is what people want... but not really - new users (any users really) don't want to memorize all that syntax for something they'll run frequently.
* Too many options
* Too long
* Often users don't even know what this is looking for
* Error prone with all the typing

Why does workbench succeed?
---------------------------

`workbench` works because users need to not learn too many new things.  Workbench is simply a wrapper script for Slurm interactive jobs that saves users from keeping too much in their personal memory or notes.

What is workbench?
------------------

```bash
$ srun -t60 -c5 --mem=50GB --gpus=1 --pty $BASH
[user@gpu1 ~]$
```

`workbench` is two scripts that essentially runs the above command but with a few more options.  Overall, `workbench` is made up of about 250 lines of code and uses a Python script and a shell script to launch jobs. 

![workbench cartoon diagram](files/workbench.png)

Features
--------
* `--help` lets people see the most important options
  * number of GPUs
  * GPU type
  * number of CPUs
  * Memory
  * Time
* Other Slurm options are fully supported
* Jupyter Notebook with port forwarding instructions
* Launch a singularity container
* Show VS Code port forwarding instructions

Requirements
------------

Slurm, Python, and Bash must be already configured on the local system.

Role Variables
--------------

N/A

Dependencies
------------

N/A

Example Playbook
----------------

- hosts: my_hosts
  gather_facts: true
  roles:
    - workbench

License
-------

GNU General Public License

Author Information
------------------

Christine Harvey, ceharvey@mitre.org