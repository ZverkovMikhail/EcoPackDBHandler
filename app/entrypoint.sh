#! /bin/bash
while ! mysqladmin ping -h mysql --silent;
do
  sleep 1
done

python main.py