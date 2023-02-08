# FROM balenalib/raspberrypi3-alpine-python:3.9.0-20201012 AS build
FROM balenalib/raspberrypi3-debian-python:3.9.0-buster-20201110 AS build
ARG TARGETPLATFORM

# RUN --mount=type=cache,id=apk-build,sharing=locked,target=/var/cache/apk \
#     mkdir -p /var/cache/apk/${TARGETPLATFORM} && \
#     ln -s /var/cache/apk/${TARGETPLATFORM} /etc/apk/cache && \
#     apk --update add git

RUN echo "Dir::Cache var/cache/apt/${TARGETPLATFORM};" > /etc/apt/apt.conf.d/01cache

RUN --mount=type=cache,id=apt-build,target=/var/cache/apt \
    mkdir -p /var/cache/apt/${TARGETPLATFORM}/archives/partial && \
    apt-get update && \
    apt-get install --no-install-recommends --yes \
        git gcc python3-dev

RUN pip install pipenv

ENV APP_DIR=/app
RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}
RUN git clone --depth 1 https://github.com/respeaker/pixel_ring.git
COPY docker/Pipfile ${APP_DIR}
# COPY docker/Pipfile.lock ${APP_DIR}
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

# FROM balenalib/raspberrypi3-alpine-python:3.9.0-run-20201012 AS runtime
FROM balenalib/raspberrypi3-debian-python:3.9.0-buster-run-20201110 AS runtime

ENV APP_DIR=/app
COPY --from=build ${APP_DIR}/ ${APP_DIR}/
COPY src ${APP_DIR}/

ENV PYTHONPATH="${APP_DIR}"
ENV PATH="${APP_DIR}/.venv/bin:$PATH"
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR ${APP_DIR}
ENTRYPOINT [ "python3", "mqtt_respeaker_pixel_ring.py"]