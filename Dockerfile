FROM python:3.10
WORKDIR /apps

ADD ./requirements.in ./requirements.in
RUN pip install -r requirements.in

ADD ./actions ./actions
ADD ./cache ./cache
ADD ./channels ./channels
ADD ./compoments ./compoments
ADD ./libs ./libs
ADD ./utils ./utils
ADD ./ops_pilot_cli.py ./ops_pilot_cli.py
ADD ./core ./core
ADD ./eventbus ./eventbus
ADD ./integrations ./integrations
ADD ./support-files/supervisor/ops-pilot.conf /etc/supervisor/conf.d/ops-pilot.conf
ADD ./support-files/supervisor/ops-pilot-action.conf /etc/supervisor/conf.d/ops-pilot-action.conf
