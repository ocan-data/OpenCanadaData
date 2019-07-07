# Conda Environments

The goal is to quickly and without fuss create an environment that can run the Open Canada software. 
To do this we use conda environments
 
## Environments
The following are the environments in this project. Each of these is represented by a yml file

| Conda Env     | Purpose              | 
| ------------- |:--------------------:| 
| ocandata    | The core evironment  | 
| ocandataml  | Core + ML            |
| ocandataviz | Core + Visualization | 


## Creating an environment
The commands below creates a new conda environment from the ocandata.yml file

`
conda env create -f ocandata.yml
`

## Updating an environment

The command below updates an existing environment

`
conda env update -f ocandata.yml
`

## Removing an environment
The command below removes a conda environment

`
conda remove --name ocandata --all
`

## Installing a Kernel into Jupyter
The command below installs a kernel for the conda environment into Jupyter

`
python -m ipykernel install --user --name ocandata --display-name "ocandata"
`
See:
https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments


### Test Cases
1. Create a conda environment from a yml file
2. Update an conda environment using a yml file. Use this: conda env update -f ocandata.yml
3. Create a kernel from each conda environment and verify that it is installed in the notebook
