FROM python:3-slim AS builder

RUN pip install --target=/app requests openziti==0.8.1

# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
COPY ./zhook.py /app/zhook.py
WORKDIR /app
ENV PYTHONPATH=/app
ENV ZITI_LOG=6
ENV TLSUV_DEBUG=6
CMD ["/app/zhook.py"]
