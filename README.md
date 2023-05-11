# Shoe-Expert

[![Docker Image CI](https://github.com/ChicoState/Shoe-Expert/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ChicoState/Shoe-Expert/actions/workflows/docker-image.yml)

## Setting Up Your Development Environment:

- The [development guide](docs/DEVELOPMENT.md) is outdated and does will not work with commits past 488b11d due to changes with the Dockerfile

    - It is still present in the repo, as some sections such as the docker buildx section and basic info on docker operations are still useful

- ~~Please read the [development guide](docs/DEVELOPMENT.md)~~
    - The Docker Buildx guide has been moved to the development guide

### Dev Container Setup

- This guide assumes you have installed [vscode](https://code.visualstudio.com/) on your system

1. Install Microsoft's [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension for vscode

2. You may also need the [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) vscode extension if not already installed

3. After reloading vscode, you should be prompted to open this repo in a dev-container after opening the Shoe-Expert folder in vscode

    - Note that you only want to run the repo inside of a docker container if you need to edit and test functionality of the django app, otherwise the dev-container is unneeded

4. The container will automatically spawn a site running on port 8000 that you can access in the browser at [localhost:8000](http://127.0.0.1:8000)

If you have a more complicated docker set-up, such as using docker in rootless mode, you can refer to the discussion in pr #28 or open up an issue in this repo if this workflow is not working correctly on your system.

## Post Container Creation

### Exit Codes

0. Success

1. Docker Container Not Detected (checks that python is PID 1)

2. createDockerAdminUser script failed (could not create superuser docker)

3. Failed to import shoe data from csv into postgres db

4. Failed to execute tests

5. Failed to generate coverage report
