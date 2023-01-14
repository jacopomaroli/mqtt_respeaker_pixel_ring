pipenv:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --python 3.9.0

act-pipenv:
	pipenv shell

install-deps:
	pipenv install paho-mqtt && pip install git+https://github.com/sn4k3/FakeRPi

docker-build-armv6:
	docker buildx build --platform linux/arm/v6 --load -t jacopomaroli/mqtt_respeaker_pixel_ring:master -f Dockerfile .

docker-run-armv6:
	docker-compose -f docker-compose-test.yml up

docker-push:
	docker push jacopomaroli/mqtt_respeaker_pixel_ring:master

save:
	docker save --output mqtt_respeaker_pixel_ring.tar jacopomaroli/mqtt_respeaker_pixel_ring:master

load:
	docker load --input mqtt_respeaker_pixel_ring.tar