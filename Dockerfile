FROM jupyter/scipy-notebook

LABEL maintainer="Theo Naunheim <theonaunheim@gmail.com"

# Back to jovyan
# Fun fact: https://github.com/jupyter/docker-stacks/issues/358
# Jovian=lives on Jupiter
# Jovyan=lives on Jupyter
USER jovyan

# Install pyfair
RUN mkdir /home/jovyan/work/src
WORKDIR /home/jovyan/work/src
RUN git clone https://github.com/theonaunheim/pyfair.git
WORKDIR /home/jovyan/work/src/pyfair
RUN pip install --no-cache-dir .
RUN rm -rf /home/jovyan/work/src

# Flip back to working environment
WORKDIR /home/jovyan/work/

#############################
# Powershell Usage
#############################

## For me to build and push

### docker build -t theonaunheim/pyfair_docker:latest .
### docker push theonaunheim/pyfair_docker:latest

## For anyone to pull and run (Windows will warn for working directory)

### docker pull theonaunheim/pyfair_docker:latest
### docker run -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes -v ${PWD}:/home/jovyan/work theonaunheim/pyfair_docker:latest

#############################
# Bash Usage
#############################

## For anyone to pull and run (PWD wrapped in braces on Powershell, parens in Bash)

### docker pull theonaunheim/pyfair_docker:latest
### docker run -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes -v $(PWD):/home/jovyan/work theonaunheim/pyfair_docker:latest
