#write into influx

export write_to_influx
function write_to_influx(influxdbbucketname,influxdbsettings,battery,powermeter)
    ##################################################################
    #Connect to InfluxDB
    ##################################################################
    #influxdbbucketname = "sonnenbatterie"
    local bucket_names 
    try
        bucket_names, json = InfluxDBClient.get_buckets(influxdbsettings);
    catch e
        @show e
        throw(ErrorException("Could not connect to InfluxDB."))
    end
    @assert in(influxdbbucketname,bucket_names) "Bucket $(influxdbbucketname) does not exist. Please create it."

    ##################################################################
    #write data to bucket. NOTE: we are using UTC timestamps
    ##################################################################

    #battery
    fields = sort(setdiff(names(battery),["datetime"]))
    tags = String[]
    rs_battery,lp = InfluxDBClient.write_dataframe(settings=influxdbsettings,bucket=influxdbbucketname,measurement="battery",data=battery,tags=tags,fields=fields,timestamp=:datetime);
    if !in(rs_battery,[200,204])
        @warn "Battery: Unexpected return value. Data may not have been written to InfluxDB" rs
    end

    #powermeter
    tags = ["direction","channel","deviceid"]
    fields = sort(setdiff(names(powermeter),vcat(tags,["datetime"])))
    rs_powermeter,lp = InfluxDBClient.write_dataframe(settings=influxdbsettings,bucket=influxdbbucketname,measurement="powermeter",data=powermeter,tags=tags,fields=fields,timestamp=:datetime);
    if !in(rs_powermeter,[200,204])
        @warn "Powermeter: Unexpected return value. Data may not have been written to InfluxDB" rs
    end

    return rs_battery,rs_powermeter
end