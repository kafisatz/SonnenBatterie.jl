export batteryTypeDict
batteryTypeDict = Dict("balancechargerequest"=>"Boolean",
"chargecurrentlimit"=>"Float",
"cyclecount"=>"Integer",
"dischargecurrentlimit"=>"Float",
"fullchargecapacity"=>"Float",
"maximumcelltemperature"=>"Float",
"maximumcellvoltage"=>"Float",
"maximumcellvoltagenum"=>"Enum",
"maximummodulecurrent"=>"Float",
"maximummoduledcvoltage"=>"Float",
"maximummoduletemperature"=>"Float",
"minimumcelltemperature"=>"Float",
"minimumcellvoltage"=>"Float",
"minimumcellvoltagenum"=>"Enum",
"minimummodulecurrent"=>"Float",
"minimummoduledcvoltage"=>"Float",
"minimummoduletemperature"=>"Float",
"relativestateofcharge"=>"Float",
"remainingcapacity"=>"Float",
"systemalarm"=>"Boolean",
"systemcurrent"=>"Float",
"systemdcvoltage"=>"Float",
"systemstatus"=>"Integer",
"systemtime"=>"Boolean",
"systemwarning"=>"Boolean",
)

#td = batteryTypeDict
for td in [batteryTypeDict]
    @assert issubset(unique(values(td)),["Boolean","Float","Integer","Enum"])
end
