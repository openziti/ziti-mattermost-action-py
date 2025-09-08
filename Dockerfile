FROM python:3.11-bullseye

WORKDIR /app
COPY ./zhook.py /app/zhook.py

RUN pip install --no-cache-dir requests openziti

ENV PYTHONPATH=/app
#ENV ZITI_LOG=6
#ENV TLSUV_DEBUG=6

CMD ["python", "/app/zhook.py"]
