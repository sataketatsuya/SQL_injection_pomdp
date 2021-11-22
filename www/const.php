<?php

# You have to set the database's ip address. This is the way to check it bellow.
# docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)
$DBuser = 'root';
$DBpass = $_ENV['MYSQL_ROOT_PASSWORD'];
$DBipaddress = '172.24.0.2';
