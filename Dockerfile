FROM --platform=$BUILDPLATFORM python:3.10-slim-bullseye

USER root
WORKDIR /root

SHELL ["/bin/bash", "-c"]

RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y --no-install-recommends install \
    apt-transport-https \
    wget \
    curl \
    ca-certificates \
    chromium-driver \
    git \
    sudo \
    libpq-dev \
    bash-completion \
    tree \
    vim \
    neofetch \
    software-properties-common && \
    apt-get -y autoclean && \
    apt-get -y autoremove

# Enable tab completion by uncommenting it from /etc/bash.bashrc
# The relevant lines are those below the phrase "enable bash completion in interactive shells"
RUN export SED_RANGE="$(($(sed -n '\|enable bash completion in interactive shells|=' /etc/bash.bashrc)+1)),$(($(sed -n '\|enable bash completion in interactive shells|=' /etc/bash.bashrc)+7))" && \
    sed -i -e "${SED_RANGE}"' s/^#//' /etc/bash.bashrc && \
    unset SED_RANGE

# Create user "docker" with sudo powers
RUN useradd -m -s /bin/bash docker && \
    usermod -aG sudo docker && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc /home/docker/

# ENV VARS for headless chromium
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium

WORKDIR /home/docker/
ENV HOME /home/docker
ENV USER docker
USER docker

# Avoid first use of sudo warning. c.f. https://askubuntu.com/a/22614/781671
RUN touch $HOME/.sudo_as_admin_successful

ADD requirements.txt /home/docker/.requirements.txt
ADD .scripts /home/docker/.local/bin/
ENV PATH /home/docker/.local/bin:$PATH
ADD .modules /home/docker/.local/custom_python_modules/
ENV PYTHONPATH /home/docker/.local/custom_python_modules:$PYTHONPATH
RUN sudo chown -R docker:root /home/docker/.local/ && \
    sudo chmod -R 775 /home/docker/.local/ && \
    sudo chmod -R 555 /home/docker/.local/custom_python_modules/

RUN pip install --user --no-cache-dir -U pip
# Note: add any new PyPi packages to requirements.txt
RUN pip install --user --no-cache-dir -r .requirements.txt
RUN printf "SECRET_KEY='%s'\n" "$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > /home/docker/.env
WORKDIR /home/docker/data/ShoeExpert
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
