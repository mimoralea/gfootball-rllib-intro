FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04
LABEL maintainer="Miguel Morales <mimoralea@gmail.com>"

ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

# Fix DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# update ubuntu installation
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
    build-essential \
    bzip2 \
    ca-certificates \
    cmake \
    curl \
    emacs \
    emacs-nox \
    ffmpeg \
    flex \
    fluidsynth \
    fonts-liberation \
    gifsicle \
    git \
    imagemagick \
    inkscape \
    jed \
    libboost-all-dev \
    libdirectfb-dev \
    libgl1-mesa-dev \
    libjpeg-dev \
    libpng-dev \
    libpq-dev \
    libsdl-sge-dev \
    libsdl2-dev \
    libsdl2-gfx-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libsm6 \
    libst-dev \
    libxext-dev \
    libxrender1 \
    lmodern \
    locales \
    mesa-utils \
    nano \
    netcat \
    nodejs \
    npm \
    pandoc \
    python-dev \
    python3-dev \
    python3-lxml \
    python3-pip \
    python3-six \
    python3-tk \
    run-one \
    sudo \
    swig \
    texlive-fonts-extra \
    texlive-fonts-recommended \
    texlive-generic-recommended \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-plain-generic \
    texlive-xetex \
    tzdata \
    unzip \
    vim \
    vim-tiny \
    wget \
    x11vnc \
    xpra \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Configure environment
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    NB_USER=$NB_USER \
    NB_UID=$NB_UID \
    NB_GID=$NB_GID \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH \
    HOME=/home/$NB_USER

# Copy a script that we will use to correct permissions after running certain commands
COPY fix-permissions /usr/local/bin/fix-permissions
RUN chmod a+rx /usr/local/bin/fix-permissions

# Enable prompt color in the skeleton .bashrc before creating the default NB_USER
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc

# Create NB_USER with name jovyan user with UID=1000 and in the 'users' group
# and make sure these dirs are writable by the `users` group.
RUN echo "auth requisite pam_deny.so" >> /etc/pam.d/su && \
    sed -i.bak -e 's/^%admin/#%admin/' /etc/sudoers && \
    sed -i.bak -e 's/^%sudo/#%sudo/' /etc/sudoers && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    mkdir -p $CONDA_DIR && \
    chown $NB_USER:$NB_GID $CONDA_DIR && \
    chmod g+w /etc/passwd && \
    fix-permissions $HOME && \
    fix-permissions $CONDA_DIR

USER $NB_UID
WORKDIR $HOME
ARG PYTHON_VERSION=3.7
ARG WITH_TORCHVISION=1

# Setup work directory for backward-compatibility
RUN mkdir /home/$NB_USER/work && \
    fix-permissions /home/$NB_USER

# Install conda as jovyan and check the md5 sum provided on the download site
ENV MINICONDA_VERSION=4.6.14 \
    MINICONDA_MD5=718259965f234088d785cad1fbd7de03 \
    CONDA_VERSION=4.6.14

WORKDIR /tmp
# https://repo.anaconda.com/miniconda/Miniconda3-4.6.14-Linux-x86_64.sh
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    echo "${MINICONDA_MD5} *Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh" | md5sum -c - && \
    /bin/bash Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    echo "conda ${CONDA_VERSION}" >> $CONDA_DIR/conda-meta/pinned && \
    conda config --system --prepend channels conda-forge && \
    conda config --system --set auto_update_conda false && \
    conda config --system --set show_channel_urls true && \
    conda config --system --set channel_priority strict && \
    if [ ! $PYTHON_VERSION = 'default' ]; then conda install --yes python=$PYTHON_VERSION; fi && \
    conda list python | grep '^python ' | tr -s ' ' | cut -d '.' -f 1,2 | sed 's/$/.*/' >> $CONDA_DIR/conda-meta/pinned && \
    conda install --quiet --yes conda && \
    conda install --quiet --yes pip && \
    conda update --all --quiet --yes && \
    conda clean --all -f -y && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Install Tini
RUN conda install --quiet --yes 'tini=0.18.0' && \
    conda list tini | grep tini | tr -s ' ' | cut -d ' ' -f 1,2 >> $CONDA_DIR/conda-meta/pinned && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Install Jupyter Notebook, Lab, and Hub
# Generate a notebook server config
# Cleanup temporary files
# Correct permissions
# Do all this in a single RUN command to avoid duplicating all of the
# files across image layers when the permissions change
RUN conda install --quiet --yes \
    'notebook=6.0.3' \
    'jupyterhub=1.1.0' \
    'jupyterlab=2.1.3' && \
    conda clean --all -f -y && \
    npm cache clean --force && \
    jupyter notebook --generate-config && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Configure container startup
# ENTRYPOINT ["tini", "-g", "--"]
# CMD ["start-notebook.sh"]

# Copy local files as late as possible to avoid cache busting
COPY start.sh start-notebook.sh start-singleuser.sh /usr/local/bin/
COPY jupyter_notebook_config.py /etc/jupyter/

# Fix permissions on /etc/jupyter as root
USER root
RUN fix-permissions /etc/jupyter/

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

# Install Python 3 packages
# Remove pyqt and qt pulled in for matplotlib since we're only ever going to
# use notebook-friendly backends in these images
# Install Python 3 packages
RUN conda install --quiet --yes \
    'beautifulsoup4=4.9.*' \
    'bokeh=2.0.*' \
    'bottleneck=1.3.*' \
    'cloudpickle=1.4.*' \
    'conda-forge::blas=*=openblas' \
    'cython=0.29.*' \
    'dask=2.15.*' \
    'dill=0.3.*' \
    'h5py=2.10.*' \
    'hdf5=1.10.*' \
    'ipympl=0.5.*'\
    'ipywidgets=7.5.*' \
    'matplotlib-base=3.2.*' \
    'numba=0.48.*' \
    'numexpr=2.7.*' \
    'pandas=1.0.*' \
    'patsy=0.5.*' \
    'protobuf=3.11.*' \
    'pytables=3.6.*' \
    'scikit-image=0.16.*' \
    'scikit-learn=0.22.*' \
    'scipy=1.4.*' \
    'seaborn=0.10.*' \
    'sqlalchemy=1.3.*' \
    'statsmodels=0.11.*' \
    'sympy=1.5.*' \
    'vincent=0.4.*' \
    'widgetsnbextension=3.5.*'\
    'xlrd=1.2.*'
RUN conda clean --all -f -y
    # Activate ipywidgets extension in the environment that runs the notebook server
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix
    # Also activate ipywidgets extension for JupyterLab
    # Check this URL for most recent compatibilities
    # https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@^2.0.0 --no-build
RUN jupyter labextension install @bokeh/jupyter_bokeh@^2.0.0 --no-build
RUN jupyter labextension install jupyter-matplotlib@^0.7.2 --no-build
RUN jupyter lab build -y --dev-build=False --minimize=False
RUN jupyter lab clean -y && \
    npm cache clean --force && \
    rm -rf "/home/${NB_USER}/.cache/yarn" && \
    rm -rf "/home/${NB_USER}/.node-gyp" && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

RUN npm i -g npm && \
    npm i -g asciicast2gif

# Install facets which does not have a pip or conda package at the moment
WORKDIR /tmp
RUN git clone https://github.com/PAIR-code/facets.git && \
    jupyter nbextension install facets/facets-dist/ --sys-prefix && \
    rm -rf /tmp/facets && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Import matplotlib the first time to build the font cache.
ENV XDG_CACHE_HOME="/home/${NB_USER}/.cache/"

RUN MPLBACKEND=Agg python -c "import matplotlib.pyplot" && \
    fix-permissions "/home/${NB_USER}"

RUN /opt/conda/bin/conda install -y python=$PYTHON_VERSION numpy pyyaml scipy ipython mkl mkl-include ninja cython typing && \
    /opt/conda/bin/conda install -y -c pytorch magma-cuda100 && \
    /opt/conda/bin/conda install -y -q -c pytorch pytorch torchvision && \
    /opt/conda/bin/conda clean -ya
ENV PATH /opt/conda/bin:$PATH

# jupyter notebook
EXPOSE 8888
# tensorboard
EXPOSE 6006

# install necessary packages
RUN pip install --upgrade pip && \
  pip install --quiet --no-cache-dir tqdm cvxpy numpy scikit-learn pyglet setuptools && \
  pip install --quiet --no-cache-dir gym asciinema pandas tabulate tornado==5.* && \
  pip install --quiet --no-cache-dir PyBullet tensorflow==2.2.0 && \
  pip install --quiet --no-cache-dir psutil && \
  pip install --quiet --no-cache-dir git+https://github.com/pybox2d/pybox2d#egg=Box2D && \
  pip install --quiet --no-cache-dir git+https://github.com/mimoralea/gym-bandits#egg=gym-bandits && \
  pip install --quiet --no-cache-dir git+https://github.com/mimoralea/gym-walk#egg=gym-walk && \
  pip install --quiet --no-cache-dir git+https://github.com/mimoralea/gym-aima#egg=gym-aima && \
  pip install --quiet --no-cache-dir gym[atari]

WORKDIR /tmp
RUN cd /tmp && \
    git clone https://github.com/google-research/football.git && \
    cd football && \
    pip install . && \
    cd && \
    rm -rf /tmp/football && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

COPY policy.xml /etc/ImageMagick-6/
COPY 1_vs_1.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 2_vs_2.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 2_vs_2_auto_GK.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 3_vs_3.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 3_vs_3_auto_GK.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 4_vs_4.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 4_vs_4_auto_GK.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/

COPY 5_vs_5.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/
COPY 5_vs_5_auto_GK.py /opt/conda/lib/python3.7/site-packages/gfootball/scenarios/

RUN pip install --upgrade pip && \
    pip uninstall -y tensorflow && \
    pip uninstall -y tensorflow-tensorboard && \
    pip uninstall -y tensorboard && \
    pip install -U tensorboardX && \
    pip install dm-tree lz4 gputil psutil && \
    pip install -U ray ray[rllib] ray[tune] ray[debug] && \
    pip install -U tensorboard && \
    pip install -U tensorflow && \
    pip install -U protobuf

# create a script to start the notebook with xvfb on the back
# this allows screen display to work well
RUN echo '#!/bin/bash' > /tmp/run.sh && \
  # echo "tensorboard --logdir /tmp/logs/ --bind_all &" >> /tmp/run.sh && \
  # echo "nohup sh -c 'tensorboard --logdir=/tmp/logs/ --bind_all' &" >> /tmp/run.sh && \
  echo "nohup sh -c 'ray start --head --include-dashboard true --dashboard-host 0.0.0.0' > /dev/null 2>&1 &" >> /tmp/run.sh && \
  echo "nohup sh -c 'tensorboard --logdir=/tmp/logs/ --bind_all' > /dev/null 2>&1 &" >> /tmp/run.sh && \
  echo 'find /mnt/notebooks/ -name "*.ipynb" -exec jupyter trust {} \;' >> /tmp/run.sh && \
  echo 'xvfb-run -s "-screen 0 1280x720x24" /usr/local/bin/start-notebook.sh' >> /tmp/run.sh && \
  chmod +x /tmp/run.sh

# make the dir with notebooks the working dir
WORKDIR /mnt/notebooks

# run the script to start the notebook
ENTRYPOINT ["/tmp/run.sh"]
