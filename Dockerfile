FROM --platform=$BUILDPLATFORM python:3.10-slim-bullseye

USER root
WORKDIR /root

SHELL ["/bin/bash", "-c"]

RUN apt-get -qq -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
    wget \
    curl \
    git \
    sudo \
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

WORKDIR /home/docker/
ADD requirements.txt /home/docker/.requirements.txt
ENV HOME /home/docker
ENV USER docker
USER docker
ENV PATH /home/docker/.local/bin:$PATH
# Avoid first use of sudo warning. c.f. https://askubuntu.com/a/22614/781671
RUN touch $HOME/.sudo_as_admin_successful
RUN pip install --upgrade pip
# Note: add any new PyPi packages to requirements.txt 
RUN pip install -r .requirements.txt

RUN printf "SECRET_KEY='%s'\n" "$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > /home/docker/.env

ENTRYPOINT ["python"]
WORKDIR /home/docker/data/ShoeExpert

CMD ["manage.py", "runserver", "0.0.0.0:8000"]
