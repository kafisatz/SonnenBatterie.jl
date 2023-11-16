using Dates; using DataFrames; using JSON3; using PyCall; using InfluxDBClient
using SonnenBatterie
using Test

@testset "SonnenBatterie.jl" begin
    @test true 

    @warn("Currently only rudimentary tests are implemented.")

    ################################################################################################
    #initilize
    ################################################################################################

    #hardcoded values
    SONNEN_USERNAME = "Installer"
    SONNEN_IP = "10.14.15.69"
    SONNEN_PASSWORD = get(ENV,"SONNEN_PASSWORD","")
    @assert length(SONNEN_PASSWORD) > 0 "SONNEN_PASSWORD environment variable is not defined"

    #the script will not run without these
    @assert haskey(ENV,"INFLUXDB_URL")
    @assert haskey(ENV,"INFLUXDB_ORG")
    @assert haskey(ENV,"INFLUXDB_TOKEN")
    influxdbsettings = InfluxDBClient.get_settings()

    @assert ENV["INFLUXDB_URL"] != ""
    @assert ENV["INFLUXDB_ORG"] != ""
    @assert ENV["INFLUXDB_TOKEN"] != ""

    @info("Testing InfluxDB access...")
    
        bucket_names, json = InfluxDBClient.get_buckets(influxdbsettings);
        @show bucket_names
        @test length(bucket_names) > 0
        @assert length(bucket_names) > 0

    #make sure that you have a bucket 'sonnenbatterie' in your InfluxDB (of course you can change the name here)
    influxdb_bucketname = "sonnenbatterie"

    nsecsleep = 30 #seconds to sleep between iterations <-> data is written ever x seconds to influxdb
    @time rs1,rs2,battery,powermeter = read_and_write(influxdbsettings,influxdb_bucketname,SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP);

    @test rs1 == 204 || rs1 == 200
    @test rs2 == 204 || rs2 == 200
            
    @test true 
end
