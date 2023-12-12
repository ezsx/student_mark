
### How to launch:

1) run docker desktop


2) go to project root


3) first build

```shell
docker build -t studentmark .
```

4) then run

```shell
docker run --name st_mark --rm -d -p 8000:8000 studentmark
```

5) then go to

``http://localhost:8000/docs``