# SonnenBatterie

## Requirements 
* InfluxDB V2 instance
* SonnenBatterie with API enabled

## Description
Reads data from SonnenBatterie (battery status and powermeter values) and writes it to an InfluxDB (V2)
You should run the lines in `infinite_loop.jl` one by one to understand how this package works
You may also want to consider run.sh which starts (or restarts) a docker container with an infinite loop to write data to InfluxDB
