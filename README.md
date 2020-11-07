# Reinforcement Learning and Decision Making

**Note:** At the moment, only running the code from the [docker](https://github.com/docker/docker-ce) container (below) is supported. Docker allows for creating a single environment that is more likely to work on all systems. Basically, I install and configure all packages for you, except docker itself, and you just run the code on a tested environment.

To install docker, I recommend a web search for "installing docker on \<your os here>". For running the code on a GPU, you have to additionally install [nvidia-docker](https://github.com/NVIDIA/nvidia-docker). NVIDIA Docker allows for using a host's GPUs inside docker containers. After you have docker (and nvidia-docker if using a GPU) installed, follow the three steps below.

## Running the code
  0. Clone this repo:
  `git clone --depth 1 https://www.github.com/mimoralea/gfootball-intro.git && cd gfootball-intro`
  1. Pull the rldm image with:
  `docker pull mimoralea/rldm:v0.4`
  2. Spin up a container:
     - On Mac or Linux:
     `docker run -it --rm --shm-size="10GB" -p 8888:8888 -p 6006:6006 -p 8265:8265 -v "$PWD"/notebooks/:/mnt/notebooks/ mimoralea/rldm:v0.4`
     - On Windows:
     `docker run -it --rm --shm-size="10GB" -p 8888:8888 -p 6006:6006 -p 8265:8265 -v %CD%/notebooks/:/mnt/notebooks/ mimoralea/rldm:v0.4`
     - NOTE: Use `nvidia-docker` if you are using a GPU.
  3. Open a browser and go to the URL shown in the terminal (likely to be: http://localhost:8888). The password is: `rldm`, Tensorboard is http://localhost:6006, Ray Dashboard is http://localhost:8265.
