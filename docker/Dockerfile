FROM docker.io/debian:stable-slim AS build

ARG swipl_version

RUN useradd -m sam

RUN \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        curl \
        build-essential cmake ninja-build pkg-config \
        ncurses-dev libedit-dev \
        libgoogle-perftools-dev \
        libgmp-dev \
        libssl-dev \
        unixodbc-dev \
        zlib1g-dev libarchive-dev \
        libossp-uuid-dev \
        libdb-dev \
        libpcre2-dev \
        libyaml-dev

WORKDIR /home/sam
USER sam

RUN \
    curl -LO https://www.swi-prolog.org/download/stable/src/swipl-${swipl_version}.tar.gz && \
    tar xf swipl-${swipl_version}.tar.gz && \
    cd swipl-${swipl_version} && \
    cmake \
        -B build \
        -G Ninja \
        -DINSTALL_DOCUMENTATION=OFF \
        -DBUILD_TESTING=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/lib/swi-prolog \
        -DCMAKE_BUILD_TYPE=PGO && \
    cmake --build build

USER root

RUN \
   cmake --install /home/sam/swipl-${swipl_version}/build


FROM docker.io/debian:stable-slim
LABEL authors="Yuce Tekol"

RUN useradd -m sam

COPY --from=build /usr/lib/swi-prolog /usr/lib/swi-prolog

RUN \
    ln -s /usr/lib/swi-prolog/bin/swipl /bin/swipl

RUN \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        libtcmalloc-minimal4t64 \
        python3

COPY ./docker/etc/update-motd.d/10-help-text /etc/update-motd.d/10-help-text
COPY ./docker/etc/update-motd.d/50-motd-news /etc/update-motd.d/50-motd-news
COPY ./src/pyswip /usr/lib/python3.13/pyswip

WORKDIR /home/sam
USER sam

ENTRYPOINT ["python3"]
