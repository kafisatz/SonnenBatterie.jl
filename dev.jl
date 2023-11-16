using Dates; using DataFrames; using JSON3; using PyCall
using SonnenBatterie

pushfirst!(PyVector(pyimport("sys")."path"), pysonnenbatteriePath)
pysonnenbatterie = pyimport("sonnenbatterie")

SONNEN_USERNAME = "Installer"
SONNEN_IP = "10.14.15.69"

SONNEN_PASSWORD = get(ENV,"SONNEN_PASSWORD","")
@assert length(SONNEN_PASSWORD) > 0 "SONNEN_PASSWORD environment variable is not defined"


#pprint(bs)

#print("\nPower:\n")
#pprint(sb.get_powermeter())
#print("\nBattery System:\n")
#pprint(sb.get_batterysystem())
#print("\nInverter:\n")
#pprint(sb.get_inverter())
#print("\nSystem Data:\n")
#pprint(sb.get_systemdata())
#print("\nStatus:\n")
#pprint(sb.get_status())
#print("\nBattery:\n")
#pprint(sb.get_battery())

#pprint(sb.get_powermeter())
#pprint(sb.get_battery())
#b = sb.get_battery()
