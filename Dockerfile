# to build the image run "docker build . --tag website"
FROM python:latest
LABEL MAINTAINER="HRLO77" LICENSE="MIT"
COPY ./* website
WORKDIR /website
ENTRYPOINT [ "python" ]
EXPOSE 8080
RUN python -m pip install -r requirements.txt
CMD ["__main__.py", 'True']
# to run a container on this image, run "docker run <IMAGE_ID>" you can get the IMAGE_ID by running "docker images"