
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

if you want to run in developer mode (hotreload with changing code), Then use this

```shell
docker run --name st_mark --rm -v D:\student_mark\app:/usr/src/app -d -p 8000:8000 studentmark uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
```

where D:\student_mark\app is you absolute path to development directory