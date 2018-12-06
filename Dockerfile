FROM python:3.7-slim
COPY . /
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python","app.py"]