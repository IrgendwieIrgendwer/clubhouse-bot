#!/bin/bash

function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

working_dir="/tmp/clubhouse"
compose="/home/admin/services/main/docker-compose.yml"

image=$(sudo docker-compose -f ${compose} config | parse_yaml | grep services_clubhouse_image | cut -d'=' -f2 | tr -d '"')
image_name=$(echo ${image} | cut -d':' -f1)
image_tag=$(echo ${image} | cut -d':' -f2)

args_version=${image_tag}
if [[ ! -z "${1}" ]]; then
  args_version="${1}"
fi

echo "Cloning Repository..."
rm -rf ${working_dir}
git clone https://github.com/thecataliastnt2k/clubhouse-bot ${working_dir}

echo "Building Docker Image..."
sudo docker build -t "local/clubhouse:${args_version}" ${working_dir}

# adjust image tag
if [[ ${image_args} != ${args_version} ]]; then
  sed -i "s|${image_name}:${image_tag}|${image_name}:${args_version}|g" ${compose}
fi


read -p "Deploy? (Strg + C to exit): "
echo "Restarting Services..."
sudo docker-compose -f ${compose} rm -fs clubhouse
sudo docker-compose -f ${compose} up -d clubhouse
sudo docker-compose -f ${compose} logs -f clubhouse

