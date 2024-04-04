#!/bin/sh
while ! mysqladmin ping -h values_db --silent;
do
  sleep 1
done

python main.py