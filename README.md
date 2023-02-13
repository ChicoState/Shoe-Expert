# Shoe-Expert

[![Docker Image CI](https://github.com/ChicoState/Shoe-Expert/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ChicoState/Shoe-Expert/actions/workflows/docker-image.yml)

## Docker Buildx

### Windows & macOS Users

- [Docker Buildx is included in Docker Desktop](https://github.com/docker/buildx#windows-and-macos)

### Linux Users

#### Redhat & Debian based distros

- [Docker Buildx is included when installing `.deb` or `.rpm` packages managed by your package manager](https://github.com/docker/buildx#linux-packages)

#### Arch based distros

- In addition to the docker package, arch-based distros require the [docker-buildx](https://archlinux.org/packages/community/x86_64/docker-buildx/) package as well.

### (All Users) Change default builder

- Set `buildx` as the [default builder](https://github.com/docker/buildx#set-buildx-as-the-default-builder) before building this repo's image by running `docker buildx install`.

## Docker Instructions:

1) clone repo
2) run "docker build -t shoe ."
3) run "docker run -it shoe"
