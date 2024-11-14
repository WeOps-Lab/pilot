push:
	git add . && codegpt commit . && git push

setup:
	virtualenv .venv -p python3.10
	./.venv/bin/pip install pip-tools

install:
	./.venv/bin/pip-compile --extra dev -v
	./.venv/bin/pip-sync -v

release:
	python -m build

train:
	NUMEXPR_MAX_THREADS=16 rasa train --domain ./data/basic/data --data ./data/basic/data -c ./data/basic/config.yml --fixed-model-name ops-pilot

online-train:
	rasa train --domain ./data/data --data ./data/data -c ./data/config.yml --fixed-model-name ops-pilot

shell:
	rasa shell --endpoints ./configs/endpoints.yml --credentials ./configs/credentials.yml

run:
    RASA_TELEMETRY_ENABLED=false rasa run --enable-api --cors "*" --endpoints ./configs/endpoints.yml --credentials ./configs/credentials.yml

online-run:
	RASA_TELEMETRY_ENABLED=false rasa run --enable-api --cors "*" --endpoints ./data/endpoints.yml --credentials ./data/credentials.yml

actions:
	rasa run actions --auto-reload

tensorboard:
	tensorboard --logdir ./tensorboard

interactive:
	rasa interactive -d data/basic/data -m models/ops-pilot.tar.gz

release:
	docker build -t etherfurnace/ops-pilot .
	docker push etherfurnace/ops-pilot

valid:
	rasa data split nlu -u data/
	rasa test nlu --nlu data/   #--cross-validation --config config_1.yml config_2.yml --runs 4 --percentages 0 25 50 70 90

finetune:
	NUMEXPR_MAX_THREADS=16 rasa train --finetune  -d data --fixed-model-name ops-pilot --epoch-fraction 0.5

visualize:
	rasa visualize -d ./data/basic/data