#!/bin/bash

# Read all parameters
while getopts "u:p:i:l:" opt; do
  case "$opt" in
    u) es_db_usr="$OPTARG" ;;
    p) es_db_pwd="$OPTARG" ;;
    i) es_db_index="$OPTARG" ;;
    l) es_db_local="${PWD}/${OPTARG}" ;;
  esac
done

# Check whether the container is created but stopped
if [ "$(docker ps -aq -f name=^/elasticsearch$)" ]; then
  echo "Elasticsearch has been stopped, trying to start..."
  docker start elasticsearch
  # Wait until the container are started
  while true; do
    #  Attempt to request index information using curl (returned 200 for success)
    response=$(curl -k -u "$es_db_usr:$es_db_pwd" -s -o /dev/null -w "%{http_code}" "https://localhost:9200/_cat/indices?v")
    if [ "$response" -eq 200 ]; then
      echo "Elasticsearch has started successfully!"
      break
    else
      echo "Elasticsearch is not yet ready, waiting..."
      sleep 5
    fi
  done
else
  echo "Elasticsearch does not exist, create and start..."
  # Local volumn for mounting
  if [ -d "$es_db_local" ]; then
    echo "The folder "$es_db_local" already exists."
  else
    echo "The folder "$es_db_local" does not exist and is being created..."
    mkdir "$es_db_local"
    echo "The folder "$es_db_local" has been created."
  fi
  # create elastic search container
  docker run -d --name elasticsearch \
    -p 9200:9200 -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
    -e "ELASTIC_PASSWORD=$es_db_pwd" \
    -v "$es_db_local":/usr/share/elasticsearch/data \
    docker.elastic.co/elasticsearch/elasticsearch:8.8.0
  # Wait until the container are created
  while true; do
    #  Attempt to request index information using curl (returned 200 for success)
    response=$(curl -k -u "$es_db_usr:$es_db_pwd" -s -o /dev/null -w "%{http_code}" "https://localhost:9200/_cat/indices?v")
    if [ "$response" -eq 200 ]; then
      echo "Elasticsearch has created successfully!"
      break
    else
      echo "Elasticsearch is not yet ready, waiting..."
      sleep 5
    fi
  done
fi
