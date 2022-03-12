FROM python:3.9.6-slim
# set work directory
ENV DEBIAN_FRONTEND noninteractive
WORKDIR /code
# copy project
COPY . /code
RUN pip install -r requirements.txt
#run app
CMD ["python", "main.py"]
