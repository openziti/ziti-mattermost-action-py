FROM python:3-slim AS builder
ADD . /app
WORKDIR /app

RUN pip install --target=/app requests openziti

# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/zhook.py"]
