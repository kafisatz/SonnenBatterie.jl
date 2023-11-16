from pprint import pprint
import os 
from sonnenbatterie.sonnenbatterie import sonnenbatterie

SONNEN_USERNAME="Installer"
SONNEN_IP="10.14.15.69"

SONNEN_PASSWORD = os.getenv('SONNEN_PASSWORD',default="")
if (SONNEN_PASSWORD is None) or (SONNEN_PASSWORD == "") or (SONNEN_PASSWORD == " "):
    print("SONNEN_PASSWORD=")
    print("SONNEN_PASSWORD")
    raise Exception('SONNEN_PASSWORD environment variable is not defined')

sb = sonnenbatterie(SONNEN_USERNAME, SONNEN_PASSWORD, SONNEN_IP)

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

#bs = b['measurements']['battery_status']
#pprint(bs)
