
export sonnen_fetch
function sonnen_fetch(SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP)
    
    pysonnenbatterie = pyimport("sonnenbatterie")
    #@show pysonnenbatterie

    #python components
    sb = pysonnenbatterie.sonnenbatterie(SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP)
    #NOTE: we are using UTC timestamps in InfluxDB
    ts = Dates.now(Dates.UTC) 
    b = sb.get_battery()
    pvec = sb.get_powermeter()

    ########################################
    #parse data
    ########################################
    
    #battery
    bs0 = b["measurements"]["battery_status"]
    bs1 = parsedict(bs0,batteryTypeDict);
    battery = DataFrame(keys(bs1) .=> values(bs1))
    battery[!, :datetime] .= ts

    #powermeter 
    #p = first(pvec)
    powermeter = DataFrame()
    for p in pvec
        #convert p to DataFrame
        df0 = DataFrame(keys(p) .=> values(p))
        append!(powermeter,df0, promote = true)
    end

    #convert to Float64
    for c in names(powermeter)
        if c in ["direction","channel","deviceid","error"] 
            continue
        end
        if !(eltype(powermeter[!,c]) <: Float64)
            powermeter[!, c] = convert.(Float64, powermeter[!, c])
        end
    end
    powermeter[!, :datetime] .= ts

    return battery,powermeter
end

