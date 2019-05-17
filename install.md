## Creating Environments

conda env create -f canadadata.yml
python -m ipykernel install --user --name canadadata --display-name "canadadata"

conda env create -f canadadataml.yml
conda env create -f canadadataviz.yml

## Installing Kernels

https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments


python -m ipykernel install --user --name canadadataml --display-name "canadadataml"
python -m ipykernel install --user --name canadadataviz --display-name "canadadataviz"