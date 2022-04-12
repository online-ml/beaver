## Taxis examples

Start a FastAPI server.

```sh
uvicorn server:app.http_server --reload
```

Alternatively, you can do this if you're developping:

```sh
uvicorn server:app.http_server --reload --reload-dir ../../
```

Upload some models.

```sh
python upload_models.py
```

Simulate traffic.

```sh
python simulate_traffic.py
```
