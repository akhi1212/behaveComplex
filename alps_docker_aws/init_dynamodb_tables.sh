#!/bin/bash

ARCHIVE_NAME=tables.tag.gz
DEFINITIONS_PATH=dynamodb-local-data
LOCAL_DYNAMO_ENDPOINT=http://localhost:4566


for f in $(find $DEFINITIONS_PATH -name "*_create.json"); do
  aws dynamodb create-table \
    --endpoint-url $LOCAL_DYNAMO_ENDPOINT \
    --cli-input-json "$(cat $f | sed -e 's/TableName": "/TableName": "DEV_/g')"
done >/dev/null 2>&1

echo "List of available dynamodb tables: $(aws dynamodb list-tables --endpoint-url $LOCAL_DYNAMO_ENDPOINT)"