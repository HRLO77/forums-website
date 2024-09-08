# to build the image run "docker build ./ --tag website" in this directory. This docker image will bind the server to 0.0.0.0 (all interfaces) on port 8000. To change the bindings, edit __main__.py and this file.
FROM python:latest
LABEL MAINTAINER="HRLO77" LICENSE="MIT"
COPY ./* website/
WORKDIR /website/
EXPOSE 8000
RUN python -m pip install -r requirements.txt
CMD ["python", "__main__.py", "--user", "qwertyazerty"]
# to run a container on this image, run "docker run --privileged <IMAGE_ID>" you can get the IMAGE_ID by running "docker images" (NOTE: you may have to start the container with the --network="host")
# to stop a running container, run "docker ps" to get a list of containers, and run "docker rm <CONTAINER_ID>"
