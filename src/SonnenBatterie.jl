module SonnenBatterie

using Dates
using DataFrames 
using PyCall
import InfluxDBClient

include("types.jl")
include("parsing.jl")

export pysonnenbatteriePath
global const pysonnenbatteriePath = normpath(joinpath(dirname(@__FILE__),"..","sonnenbatterie"))
#pysonnenbatteriePath = normpath(joinpath(dirname(pathof(SonnenBatterie)),"..","sonnenbatterie"))
@assert isdir(pysonnenbatteriePath)
pushfirst!(PyVector(pyimport("sys")."path"), pysonnenbatteriePath)
pysonnenbatterie = pyimport("sonnenbatterie")

function __init__()
    @assert isdir(pysonnenbatteriePath)
    pushfirst!(PyVector(pyimport("sys")."path"), pysonnenbatteriePath)
    pysonnenbatterie = pyimport("sonnenbatterie")
    return nothing
end

include("fetch.jl")
include("write.jl")

#core warpper function
export read_and_write
function read_and_write(influxdbsettings,influxdb_bucketname,SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP)
    ################################################################################################
    #read data
    ################################################################################################
    battery,powermeter = sonnen_fetch(SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP)

    ################################################################################################
    #write to influxdb
    ################################################################################################
    rs1,rs2 = write_to_influx(influxdb_bucketname,influxdbsettings,battery,powermeter)
    return rs1,rs2,battery,powermeter
end

end