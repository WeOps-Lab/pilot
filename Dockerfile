FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y libhdf5-dev vim python3 python3-pip unzip curl pkg-config libssl-dev libffi-dev supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /apps

ADD . .

RUN pip install pip-tools
RUN pip-compile --extra dev -v
RUN pip install -r requirements.txt
RUN python3 -m build
RUN mv ./dist /tmp
RUN cp ./cli.py /tmp/cli.py
RUN rm -Rf ./*
RUN pip install /tmp/dist/*.whl
RUN mv /tmp/cli.py . 
RUN rm -Rf /tmp/dist

ADD ./support-files/supervisor/ops-pilot.conf /etc/supervisor/conf.d/ops-pilot.conf
ADD ./support-files/supervisor/ops-pilot-action.conf /etc/supervisor/conf.d/ops-pilot-action.conf
