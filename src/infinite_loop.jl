using Dates; using DataFrames; using JSON3; using PyCall; using InfluxDBClient
using SonnenBatterie

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
try
    bucket_names, json = InfluxDBClient.get_buckets(influxdbsettings);
    @show bucket_names
    @assert length(bucket_names) > 0
catch e
    @show e
    @warn("Failed to access InfluxDB. See above!")
end

#make sure that you have a bucket 'sonnenbatterie' in your InfluxDB (of course you can change the name here)
influxdb_bucketname = "sonnenbatterie"

nsecsleep = 5 #seconds to sleep between iterations <-> data is written ever x seconds to influxdb
while true
    try
        @time rs1,rs2,battery,powermeter = read_and_write(influxdbsettings,influxdb_bucketname,SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP);
        powermeter[:,:kwh_exported]
        @info("$(Dates.now()) - Return values - Battery: $(rs1), Powermeter: $(rs2)")
    catch er
        @show er
    end
    sleep(nsecsleep)
end

