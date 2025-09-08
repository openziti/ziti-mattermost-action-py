docker run --rm -it \
  -v "$PWD":/app -w /app \
  -e INPUT_ZITIID="$(< /tmp/zmm.json)" \
  --env-file ./zmm.env \
  zmm