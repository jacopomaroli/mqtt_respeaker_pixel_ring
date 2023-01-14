# -----------------------------------------------------------------------------
# Dockerfile for MQTT reaspeaker pixel ring (https://github.com/jacopomaroli/mqtt_respeaker_pixel_ring)
# Requires Docker buildx: https://docs.docker.com/buildx/working-with-buildx/
# See Makefile
#
# Builds a multi-arch image for amd64/armv6/armv7/arm64.
# The virtual environment from the build stage is copied over to the run stage.
# The MQTT reaspeaker pixel ring source code is then copied into the run stage and executed within
# that virtual environment.
#
# Build stages are named build-$TARGETARCH$TARGETVARIANT, so build-amd64,
# build-armv6, etc. Run stages are named similarly.
#
# armv6 images (Raspberry Pi 0/1) are derived from balena base images:
# https://www.balena.io/docs/reference/base-images/base-images/#balena-base-images
# -----------------------------------------------------------------------------

# Build stage for amd64/armv7/arm64
FROM debian:buster as build-debian
ARG TARGETARCH
ARG TARGETVARIANT

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN echo "Dir::Cache var/cache/apt/${TARGETARCH}${TARGETVARIANT};" > /etc/apt/apt.conf.d/01cache

RUN --mount=type=cache,id=apt-build,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETARCH}${TARGETVARIANT}/archives/partial && \
    apt-get update && \
    apt-get install --no-install-recommends --yes \
        python3 python3-dev python3-setuptools python3-pip python3-venv \
        build-essential cython curl wget ca-certificates pipenv virtualenv

# -----------------------------------------------------------------------------

FROM build-debian as build-amd64

FROM build-debian as build-armv7
ARG TARGETARCH
ARG TARGETVARIANT

RUN --mount=type=cache,id=apt-build,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETARCH}${TARGETVARIANT}/archives/partial && \
    apt-get install --no-install-recommends --yes \
        git

FROM build-debian as build-arm64
ARG TARGETARCH
ARG TARGETVARIANT

RUN --mount=type=cache,id=apt-build,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETARCH}${TARGETVARIANT}/archives/partial && \
    apt-get install --no-install-recommends --yes \
        git

# -----------------------------------------------------------------------------

# Build stage for armv6
FROM balenalib/raspberry-pi-debian-python:3.9.0-buster-20201118 as build-armv6
ARG TARGETARCH
ARG TARGETVARIANT

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN echo "Dir::Cache var/cache/apt/${TARGETARCH}${TARGETVARIANT};" > /etc/apt/apt.conf.d/01cache

RUN --mount=type=cache,id=apt-build,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETARCH}${TARGETVARIANT}/archives/partial && \
    install_packages \
        cython ca-certificates git python3-venv

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

ARG TARGETARCH
ARG TARGETVARIANT
FROM build-$TARGETARCH$TARGETVARIANT as build
ARG TARGETARCH
ARG TARGETVARIANT

RUN pip install --upgrade virtualenv pipenv

# Install python dependencies in /.venv
ENV APP_DIR=/app
RUN mkdir -p ${APP_DIR}
RUN cd ${APP_DIR} && git clone --depth 1 https://github.com/respeaker/pixel_ring.git
COPY Pipfile ${APP_DIR}
COPY Pipfile.lock ${APP_DIR}
RUN cd ${APP_DIR} && PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

# Clean up
RUN rm -f /etc/apt/apt.conf.d/01cache

# -----------------------------------------------------------------------------

# Run stage for amd64/armv7/arm64
FROM debian:buster as run-debian
ARG TARGETARCH
ARG TARGETVARIANT

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN echo "Dir::Cache var/cache/apt/${TARGETARCH}${TARGETVARIANT};" > /etc/apt/apt.conf.d/01cache

RUN --mount=type=cache,id=apt-run,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETARCH}${TARGETVARIANT}/archives/partial && \
    apt-get update && \
    apt-get install --yes --no-install-recommends \
        python3 libpython3.9 python3-pip python3-setuptools python3-distutils \
        curl wget ca-certificates

FROM run-debian as run-amd64

FROM run-debian as run-armv7

FROM run-debian as run-arm64

# -----------------------------------------------------------------------------

# Run stage for armv6
FROM balenalib/raspberry-pi-debian-python:3.9.0-buster-run-20201118 as run-armv6
ARG TARGETARCH
ARG TARGETVARIANT

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN echo "Dir::Cache var/cache/apt/${TARGETARCH}${TARGETVARIANT};" > /etc/apt/apt.conf.d/01cache

RUN --mount=type=cache,id=apt-run,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETARCH}${TARGETVARIANT}/archives/partial && \
    install_packages \
        curl wget ca-certificates

# Clean up
RUN rm -f /etc/apt/apt.conf.d/01cache

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------

ARG TARGETARCH
ARG TARGETVARIANT
FROM run-$TARGETARCH$TARGETVARIANT
ARG TARGETARCH
ARG TARGETVARIANT

RUN pip install --upgrade virtualenv pipenv

ENV APP_DIR=/app
COPY --from=build ${APP_DIR}/ ${APP_DIR}/
COPY src ${APP_DIR}/

ENV PYTHONPATH "${APP_DIR}"
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /app
ENTRYPOINT [ "pipenv", "run", "python3", "mqtt_respeaker_pixel_ring.py"]