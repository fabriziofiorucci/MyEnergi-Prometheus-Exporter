# MyEnergi Prometheus Exporter

This is a [Prometheus](https://prometheus.io/) exporter for [myenergi](https://www.myenergi.com/) renewable energy products.

# Prerequisites

- Docker 23.0+
- Kubernetes cluster
- Myenergi API Key - this can be created through [https://myaccount.myenergi.com/](https://myaccount.myenergi.com/)
- Myenergi Eddi and/or Harvi

# Support

Modules currently implemented are:

- [X] Eddi
- [X] Harvi
- [ ] Zappi
- [ ] Libbi

# Getting an API Key

This repository requires a Myenergi API Key. It can be created through [https://myaccount.myenergi.com/](https://myaccount.myenergi.com/)

# Building the image

The docker image can be built using:

```
docker build -t myenergi:latest .
```

# Running on Kubernetes

1. Configure the relevant fields in the [Kubernetes manifest](/contrib/kubernetes)
- `<DOCKER_IMAGE_NAME>` - The docker image (ie. `myenergi:latest`)
- `<MYENERGI_USERNAME>` - Your Myenergi username
- `<MYENERGI_API_KEY>` - Your Myenergi API key
- `<MYENERGI_SERVER>` - Your Myenergi server (format must be `https://<FQDN>`, default `https://s18.myenergi.net`)
- `<YOUR_PREFERRED_FQDN>` - The fully qualified domain name to access the container through the Kubernetes ingress controller

2. Deploy the manifest:

```
kubectl apply -f contrib/kubernetes/myenergi-prometheus.yaml
```

3. Test the prometheus scraping endpoint:

```
curl http://<YOUR_PREFERRED_FQDN>
```
