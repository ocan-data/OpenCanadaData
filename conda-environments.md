# Conda Environments

The goal is to quickly and without fuss create an environment that can run the Open Canada software. 
To do this we use conda environments
 
## Environments
The following are the environments in this project. Each of these is represented by a yml file

| Conda Env     | Purpose              | 
| ------------- |:--------------------:| 
| canadadata    | The core evironment  | 
| canadadataml  | Core + ML            |
| canadadataviz | Core + Visualization | 


## Creating an environment
The commands below creates a new conda environment from the canadadata.yml file

`
conda env create -f canadadata.yml
`

## Updating an environment

The command below updates an existing environment

`
conda env update -f canadadata.yml
`

## Removing an environment
The command below removes a conda environment

`
conda remove --name canadadata --all
`

## Installing a Kernel into Jupyter
The command below installs a kernel for the conda environment into Jupyter

`
python -m ipykernel install --user --name canadadata --display-name "canadadata"
`
See:
https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments


### Test Cases
1. Create a conda environment from a yml file
2. Update an conda environment using a yml file. Use this: conda env update -f canadadata.yml
3. Create a kernel from each conda environment and verify that it is installed in the notebook
