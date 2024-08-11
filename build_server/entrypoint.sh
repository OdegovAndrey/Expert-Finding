#!/bin/bash

if [[ ! -f "data.pqt" ]]; then
  echo "data.pqt is required!"
  exit 1;
fi

if [[ ! -f "$PATH_TO_DATA" ]]; then
  echo "$PATH_TO_DATA is required!"
  exit 1;
fi

exec "$@"

