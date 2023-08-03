#!/bin/bash
#

images_dir=/tmp/docker_images
mkdir -p $images_dir
image_list="python:3.9-slim alpine python:3.9-alpine traefik hashicorp/vault"
for each in $image_list
do
  docker image pull $each;
  each2=`echo $each | sed s/"\/"/"-"/g `
  docker save $each > $images_dir/$each2
done


# If the packagelist are known, then we don't need to build each docker container and just use

cont=certauth
apk_url=http://dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64/
file_list_name=apk_file_list
format=apk
mkdir ${cont}/${format}
for each in `more ${cont}/${file_list_name}`
do wget $apk_url$each -P${cont}/${format} ; done

tag=ap_copy_things
# Certauth

list="make openssl"
docker run -d --rm --name $tag alpine /bin/sh -c "mkdir -p /apk && cd /apk && apk update && apk fetch -R $list && tail -f /dev/null"
docker exec $tag /bin/sh -c "cd /apk && apk fetch -R python3 py-pip docker openrc && tail -f /dev/null"
sleep 10

# Unsealer
docker exec $tag /bin/sh -c "cd /apk && apk fetch -R python3 py-pip docker openrc && tail -f /dev/null"
sleep 30

docker cp $tag:/apk $images_dir




docker stop $tag

tag=py_copy_things
list="build-essential inetutils-ping"
docker run -d --rm --name $tag python:3.9-slim /bin/bash -c "mkdir -p /deb && cd /deb && apt-get update && \
       	apt-get install --dry-run --no-install-recommends ${list} > /tmp/apt_list && \
       	sed -n '/The following NEW packages will be installed:/,/upgraded/p' /tmp/apt_list | tail -n+2 | head -n-1 | tr '\n' ' ' > /tmp/apt_list2 && \
	tail -f /dev/null"

docker exec $tag /bin/sh -c "cd /deb && cat /tmp/apt_list2  | xargs apt-get download"
sleep 60
docker cp $tag:/deb $images_dir
