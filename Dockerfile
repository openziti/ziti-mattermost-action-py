FROM python:3-slim AS builder

COPY requirements.txt /tmp/requirements.txt
RUN pip install --target=/app --requirement /tmp/requirements.txt

# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
COPY --chmod=0755 ./zhook.py /app/zhook.py
WORKDIR /app
ENV PYTHONPATH=/app

CMD ["/app/zhook.py"]
