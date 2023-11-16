export parsedict
function parsedict(di,typedict)
    #=
        di = bs
        typedict = batteryTypeDict
        unique(values(typedict))
    =#
    d = Dict{String,Any}()
    for (k,v) in di
        if haskey(typedict,k)
            if typedict[k] == "Float"                
                d[k] = parse(Float64,v)
            else 
                #enum, bool and and integers are treated as integers for now 
                d[k] = parse(Int,v)
            end
        else 
            d[k] = v
        end
    end
return d
end