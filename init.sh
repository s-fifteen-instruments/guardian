#!/bin/sh


docker-compose up -d --build certauth
sleep 1
docker-compose logs certauth
docker-compose up -d vault
sleep 1
docker-compose logs vault
docker-compose up -d --build vault_init
sleep 2
docker-compose logs vault_init
docker-compose up -d --build certauth_csr
sleep 1
docker-compose logs certauth_csr
