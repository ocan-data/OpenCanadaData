set conda_env_file=%1
set filename=%~n1
set extension=%~x1

GET_CONDA_ENV_NAME = "import sys; from ruamel.yaml import YAML; yaml = YAML(typ='safe')"
if exist "%conda_env_file%" (
if "%extension%" == ".yml" (
    set env_name=python loadenv.py "%conda_env_file%"
    echo %env_name%
 )
)