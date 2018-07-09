#!/bin/bash
pkill -F cassandra.pid
kill -9 $(netstat -tlnp | grep :7199 | awk '{print $7}' | awk -F '/' '{print $1}')
echo "stop cassandra"
/usr/local/cassandra/bin/cassandra -p cassandra.pid > dawncass.log 2>&1
echo "restart is over start to test"