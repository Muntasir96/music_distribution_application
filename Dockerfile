FROM python:3.7-slim
ADD . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python","app.py"]