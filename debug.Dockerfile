FROM zhook-action AS distroless

FROM python:3-slim AS debug

COPY --from=distroless /app /app

RUN apt-get update && apt-get install -y valgrind
