FROM python:3.8-alpine3.10

ENV PYTHONUNBUFFERED 1
WORKDIR /usr/workspace

COPY . .

ENTRYPOINT ["python", "metrics2csv.py", "-o", "output/output.csv"]
