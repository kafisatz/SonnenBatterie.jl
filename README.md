# SonnenBatterie

[![Build Status](https://github.com/kafisatz/SonnenBatterie.jl/actions/workflows/CI.yml/badge.svg?branch=master)](https://github.com/kafisatz/SonnenBatterie.jl/actions/workflows/CI.yml?query=branch%3Amaster)

## Requirements 
* InfluxDB V2 instance
* SonnenBatterie with API enabled

## Description
Reads data from SonnenBatterie (battery status and powermeter values) and writes it to an InfluxDB (V2)
You should run the lines in `infinite_loop.jl` one by one to understand how this package works

