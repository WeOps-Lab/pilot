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

RUN cd ./dist && unzip *.whl
RUN cp ./cli.py /tmp/cli.py

RUN rm -Rf ./actions/*
RUN touch ./actions/__init__.py
RUN mv ./dist/actions* ./actions/

RUN rm -Rf ./channels/*
RUN touch ./channels/__init__.py
RUN mv ./dist/channels* ./channels/

RUN rm -Rf ./compoments/*
RUN touch ./compoments/__init__.py
RUN mv ./dist/compoments* ./compoments/

RUN rm -Rf ./core/*
RUN touch ./core/__init__.py
RUN mv ./dist/core* ./core/

RUN rm -Rf ./custom_broker/*
RUN touch ./custom_broker/__init__.py
RUN mv ./dist/custom_broker* ./custom_broker/

RUN rm -Rf ./eventbus/*
RUN touch ./eventbus/__init__.py
RUN mv ./dist/eventbus* ./eventbus/

RUN rm -Rf ./libs/*
RUN touch ./libs/__init__.py
RUN mv ./dist/libs* ./libs/

RUN rm -Rf ./utils/*
RUN touch ./utils/__init__.py
RUN mv ./dist/utils* ./utils/

RUN rm -Rf ./dist
RUN rm -Rf ./tests

ADD ./support-files/supervisor/ops-pilot.conf /etc/supervisor/conf.d/ops-pilot.conf
ADD ./support-files/supervisor/ops-pilot-action.conf /etc/supervisor/conf.d/ops-pilot-action.conf
