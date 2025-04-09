
## Dockerized Example App

### Run machine

Build image
```bash
docker build -t machine ./machine
```

Run machien image as container
```bash
docker run -ti --env API_URL=http://host.docker.internal:8000 machine
```
### Run frontend

Build image
```bash
docker build -t frontend ./frontend
```

Run frontend image as container
```bash
docker run -ti -p 3000:3000 frontend
```
