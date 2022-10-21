# to build the image run "docker build . --tag website"
FROM python:latest
LABEL MAINTAINER="HRLO77" LICENSE="MIT"
COPY ./* website/
WORKDIR /website/
# EXPOSE 8000
RUN python -m pip install -r requirements.txt
CMD ["python", "__main__.py", "True"]
# to run a container on this image, run "docker run -p 8000:8000 --privileged --network="host" <IMAGE_ID>" you can get the IMAGE_ID by running "docker images"