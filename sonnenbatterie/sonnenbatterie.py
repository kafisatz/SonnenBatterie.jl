import requests
import hashlib
import json

from datetime import time
#from requests import Timeout


"""Process the time of use schedule stuff"""
from datetime import time, datetime
from typing import List

############################################################################################################
#timeofuse.py
############################################################################################################        

ATTR_TOU_START="start"
ATTR_TOU_STOP="stop"
ATTR_TOU_MAX_POWER="threshold_p_max"
TIME_FORMAT="%H:%M"

MIDNIGHT=time()

class timeofuse:
    def __init__(self, start_time:time, stop_time:time, max_power=20000):
        self.start_time = start_time
        # for comparisson reasons we can't have the stop time be midnight as thaty's actually the earliest possible time
        # so if it is provided as midnight make it the latest possible time
        if (stop_time == MIDNIGHT):
            stop_time = time.max
        self.stop_time = stop_time
        self.max_power = max_power

    def __eq__(self, other) -> bool :
        if not isinstance(other, type(self)):
            return False
        return (self.start_time == other.start_time) and (self.stop_time == other.stop_time) and (self.max_power == other.max_power) 

    def __hash__(self) -> int:
        return hash(self.start_time) ^ hash(self.stop_time) ^ hash(self.max_power)

    def get_as_tou(self):
        start_string = self.get_start_time_as_string()
        tmp_stop_time = self.stop_time
        # previously we had to munge midnight as an stop time to 23:59:59.999999
        # if that was done now undo it
        if (tmp_stop_time == time.max):
            tmp_stop_time = MIDNIGHT

        stop_string=tmp_stop_time.strftime(TIME_FORMAT)
        max_power_string = str(self.max_power)
        return {ATTR_TOU_START:start_string, ATTR_TOU_STOP:stop_string, ATTR_TOU_MAX_POWER:max_power_string}
    
    def get_as_string(self) -> str:
        resp = "Start "+self.get_start_time_as_string()+", End "+self.get_stop_time_as_string(), "Max allowable power "+str(self.get_max_power())
        return resp 

    def get_start_time_as_string(self) -> str:
        return self._get_time_as_string(self.start_time)
    
    def get_stop_time_as_string(self) -> str:
        tmp_stop_time = self.stop_time
        # previously we had to munge midnight as an stop time to 23:59:59.999999
        # if that was done now undo it
        if (tmp_stop_time == time.max):
            tmp_stop_time = MIDNIGHT
        return self._get_time_as_string(tmp_stop_time)
    
    def _get_time_as_string(self, timeobj:time) -> str:
        return timeobj.strftime(TIME_FORMAT)
    
    def get_max_power(self) -> int:
        return self.max_power
    
    def from_tou(tou):
        # parse it out
        start_time = datetime.strptime(tou.get(ATTR_TOU_START), TIME_FORMAT).time()
        stop_time = datetime.strptime(tou.get(ATTR_TOU_STOP), TIME_FORMAT).time()
        max_power= int(tou.get(ATTR_TOU_MAX_POWER))
        # build the resulting object
        return timeofuse(start_time, stop_time, max_power)
    
    def is_overlapping(self, other):
        # is our start time within the others time window ?
        if (self.start_time>= other.start_time) and (self.start_time<= other.stop_time):
            return True
        
        # is our end time within the others time window ?
        if (self.stop_time>= other.start_time) and (self.stop_time<= other.stop_time):
            return True
        

        # is it's start time within the out time window ?
        if (other.start_time>= self.start_time) and (other.start_time<= self.stop_time):
            return True
        
        # is it's end time within the out time window ?
        if (other.stop_time>= self.start_time) and (other.stop_time<= self.stop_time):
            return True
        
        # no overlap
        return False
    
    def create_time_of_use_entry(start_hour=23, start_min=30, stop_hour=5, stop_min=30, max_power=20000):
        start_time = time(hour=start_hour, minute=start_min)
        stop_time = time(hour=stop_hour, minute=stop_min) 
        return timeofuse(start_time, stop_time, int(max_power))
    
class timeofuseschedule:
    def __init__(self):
        self._schedule_entries = []

    # adds the entry ensureing that it does not overlap with an existing entry
    def _add_entry(self, entry):
        if (entry.stop_time < entry.start_time):
            raise Exception("End time cannot be before start time")
        for i in self._schedule_entries:
            if (i.is_overlapping(entry)):
                raise Exception("Unable to add entry, overlaps with exisitngv entry")
        self._schedule_entries.append(entry)
        # maintains this as a sotred list based on the start time, this lets us compare properly
        self._schedule_entries = sorted(self._schedule_entries, key=lambda entry: entry.start_time)

    # Add an entry, if it spans midnight split it into a before midnight and after midnight section
    # Note that this IS NOT reversed on retrieving the saved entries
    # Note that the change may result in a modified list order, so callers should AWAYS
    # use the returned list or get a new one as that will reflect the current state of
    # afairs
    def add_entry(self, entry):
        if (entry.start_time > entry.stop_time):
            # this is a over midnight situation
            self._add_entry(timeofuse(entry.start_time, time.max, entry.max_power))
            self._add_entry(timeofuse(time.min, entry.stop_time,entry.max_power))
        else:
            self._add_entry(entry)
        return self.get_as_tou_schedule()

    # Note that the change may result in a modified list order, so callers should AWAYS
    # use the returned list or get a new one as that will reflect the current state of
    # afairs
    def delete_entry(self, entry_number):
        self._schedule_entries.pop(entry_number)
        return self.get_as_tou_schedule()
    # removes and exisitng entry and adds a new one , this is really just a convenience
    # If the new entry is rejected due to overlap then the deleted one IS NOT REPLACED
    # Note that the change may result in a modified list order, so callers should AWAYS
    # use the returned list or get a new one as that will reflect the current state of
    # afairs
    def remove_and_replace_entry(self, old_entry_nuber, new_entry):
        self._schedule_entries.pop(old_entry_nuber)
        return self.add_entry(new_entry)

    def get_as_tou_schedule(self)-> List[timeofuse]:
        schedules = []
        for i in self._schedule_entries :
            schedules.append(i.get_as_tou())
        return schedules
    
    def get_as_string(self) -> str:
        result = ""
        doneFirst = False 
        for entry in self._schedule_entries :
            if (doneFirst) :
                result = result +","
            else :
                doneFirst = True 
            result = result + str(entry.get_as_string())
        return result 
    
    # retained fore compatibility purposed, is not just a wrapper roung  def load_tou_schedule
    def load_tou_schedule(self, schedcule):
        self.load_tou_schedule_from_json(schedcule)

    # replace the current tou schedule data with the new dicitonary data
    def load_tou_schedule_from_json(self, json_schedule):
        self._schedule_entries = []
        for entry in json_schedule:
            tou_entry = timeofuse.from_tou(entry)
            self.add_entry(tou_entry)

    # create a new timeofuseschedule with the provided array ofdictionary data
    def build_from_json(json_schedule) :
        tous = timeofuseschedule()
        for entry in json_schedule:
            tou_entry = timeofuse.from_tou(entry)
            tous.add_entry(tou_entry)
        return tous
    
    def entry_count(self) -> int:
        return len(self._schedule_entries)

    
    def get_tou_entry_count(self) -> int:
        return len(self._schedule_entries)
    
    def get_tou_entry(self, i:int) -> timeofuse:
        entrties = self.get_tou_entry_count()
        if (i > entrties):
            return None
        else:
            return self._schedule_entries[i]

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        myEntryCount = self.entry_count() 
        otherEntryCount = other.entry_count()
        # if there both zero length by definition they are equal
        if (myEntryCount == 0) and (otherEntryCount==0):
            return True
        # different numbers of entries means different scheduled
        if (myEntryCount != otherEntryCount):
            return False
        # for each entry
        for i in range(0, myEntryCount):
            myTou = self.get_tou_entry(i)
            otherTou = other.get_tou_entry(i)
            if (myTou != otherTou):
                return False
        # got to the end of the individual timeofuse entries and they arew all equal so ...
        return True
    
    def __hash__(self) -> int:
        myHash = 0
        myEntryCount = self.entry_count() 
        for i in range(0, myEntryCount):
            myTou = self.get_tou_entry(i)
            myTouHash = hash(myTou) 
            # adjust the hash based on the position in the order to allow for things in a differing order
            myHash = myHash ^ (myTouHash + i)
        return myHash



############################################################################################################
#const.py
############################################################################################################        
DEFAULT_BATTERY_LOGIN_TIMEOUT=120
DEFAULT_CONNECT_TO_BATTERY_TIMEOUT=60
DEFAULT_READ_FROM_BATTERY_TIMEOUT=60

SONNEN_OPERATING_MODE_UNKNOWN_NAME="Unknown Operating Mode"
SONNEN_OPERATING_MODE_UNKNOWN="0"
SONNEN_OPERATING_MODE_MANUAL_NAME="Manual"
SONNEN_OPERATING_MODE_AUTOMATIC_SELF_CONSUMPTION_NAME="Automatic - Self-Consumption"
SONNEN_OPERATING_MODE_BATTERY_MODULE_EXTENSION_30_PERCENT_NAME="Battery-Module-Extension (30%)"
SONNEN_OPERATING_MODE_TIME_OF_USE_NAME="Time-Of-Use"
SONNEN_OPERATING_MODE_NAMES_TO_OPERATING_MODES =  {SONNEN_OPERATING_MODE_MANUAL_NAME :"1", SONNEN_OPERATING_MODE_AUTOMATIC_SELF_CONSUMPTION_NAME:"2", SONNEN_OPERATING_MODE_BATTERY_MODULE_EXTENSION_30_PERCENT_NAME:"6", SONNEN_OPERATING_MODE_TIME_OF_USE_NAME:"10"}
SONNEN_OPERATING_MODES_TO_OPERATING_MODE_NAMES= {v:k for k,v in SONNEN_OPERATING_MODE_NAMES_TO_OPERATING_MODES.items()}

SONNEN_OPEATING_MODES=[SONNEN_OPERATING_MODE_MANUAL_NAME, SONNEN_OPERATING_MODE_AUTOMATIC_SELF_CONSUMPTION_NAME, SONNEN_OPERATING_MODE_BATTERY_MODULE_EXTENSION_30_PERCENT_NAME,SONNEN_OPERATING_MODE_TIME_OF_USE_NAME ]

SONNEN_CONFIGURATION_OPERATING_MODE="EM_OperatingMode"
SONNEN_CONFIGURATION_TOU_SCHEDULE="EM_ToU_Schedule"
SONNEN_CONFIGURATION_BACKUP_RESERVE="EM_USOC"
SONNEN_LATEST_DATA_CHARGE_LEVEL="USOC"

SONNEN_API_PATH_CONFIGURATIONS="v2/configurations"
SONNEN_API_PATH_LATEST_DATA="v2/latestdata"
SONNEN_API_PATH_POWER_METER="powermeter"
SONNEN_API_PATH_BATTERY_SYSTEM="battery_system"
SONNEN_API_PATH_INVERTER="inverter"
SONNEN_API_PATH_SYSTEM_DATA="system_data"
SONNEN_API_PATH_STATUS="v1/status"
SONNEN_API_PATH_BATTERY="battery"

SONNEN_CHARGE_PATH="charge"
SONNEN_DISCHARGE_PATH="discharge"






############################################################################################################
#sonnenbatterie.py - Python API for the sonnenBatterie
############################################################################################################       
#from .timeofuse import timeofuseschedule

class sonnenbatterie:
    def __init__(self,username,password,ipaddress):
        self.username=username
        self.password=password
        self.ipaddress=ipaddress
        self.baseurl='http://'+self.ipaddress+'/api/'
        self.setpoint='v2/setpoint/'
        self._batteryLoginTimeout = DEFAULT_BATTERY_LOGIN_TIMEOUT 
        self._batteryConnectTimeout = DEFAULT_CONNECT_TO_BATTERY_TIMEOUT 
        self._batteryReadTimeout = DEFAULT_READ_FROM_BATTERY_TIMEOUT 
        self._batteryRequestTimeout = (self._batteryConnectTimeout, self._batteryReadTimeout)

        self._login()


    def _login(self):
        password_sha512 = hashlib.sha512(self.password.encode('utf-8')).hexdigest()
        req_challenge=requests.get(self.baseurl+'challenge', timeout=self._batteryLoginTimeout)
        req_challenge.raise_for_status()
        challenge=req_challenge.json()
        response=hashlib.pbkdf2_hmac('sha512',password_sha512.encode('utf-8'),challenge.encode('utf-8'),7500,64).hex()
        
        #print(password_sha512)
        #print(challenge)
        #print(response)
        getsession=requests.post(self.baseurl+'session',{"user":self.username,"challenge":challenge,"response":response}, timeout=self._batteryLoginTimeout)
        getsession.raise_for_status()
        #print(getsession.text)
        token=getsession.json()['authentication_token']
        #print(token)
        self.token=token

    def set_login_timeout(self, timeout:int = 120):
        self._batteryLoginTimeout = timeout
    
    def get_login_timeout(self) -> int:
        return self._batteryLoginTimeout
    
    def set_request_connect_timeout(self, timeout:int = 60):
        self._batteryConnectTimeout = timeout
        self._batteryRequestTimeout = (self._batteryConnectTimeout, self._batteryReadTimeout)

    def get_request_connect_timeout(self) -> int:
        return self._batteryConnectTimeout
    
    def set_request_read_timeout(self, timeout:int = 60):
        self._batteryReadTimeout = timeout
        self._batteryRequestTimeout = (self._batteryConnectTimeout, self._batteryReadTimeout)

    def get_request_read_timeout(self) -> int:
        return self._batteryReadTimeout
    
    def _get(self,what,isretry=False):
        # This is a synchronous call, you may need to wrap it in a thread or something for asynchronous operation        
        url = self.baseurl+what
        response=requests.get(url,
            headers={'Auth-Token': self.token}, timeout=self._batteryRequestTimeout
        )
        if not isretry and response.status_code==401:
            self._login()
            return self._get(what,True)
        if response.status_code != 200:
            response.raise_for_status()

        return response.json()    

    def _put(self, what, payload, isretry=False):
        # This is a synchronous call, you may need to wrap it in a thread or something for asynchronous operation
        url = self.baseurl+what
        response=requests.put(url,
            headers={'Auth-Token': self.token,'Content-Type': 'application/json'} , json=payload, timeout=self._batteryRequestTimeout
        )
        if not isretry and response.status_code==401:
            self._login()
            return self._put(what, payload,True)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    def _post(self, what, isretry=False):
        # This is a synchronous call, you may need to wrap it in a thread or something for asynchronous operation
        url = self.baseurl+what
        print("Posting "+url)
        response=requests.post(url,
            headers={'Auth-Token': self.token,'Content-Type': 'application/json'}, timeout=self._batteryRequestTimeout
        )
        if not isretry and response.status_code==401:
            self._login()
            return self._post(what, True)
        if response.status_code != 200:
            response.raise_for_status()
        return response
    
    # these are special purpose endpoints, there is no associated data that I'm aware of
    # while I don't have details I belive this is probabaly only useful in manual more
    # and it's probabaly possible to extact the actuall flow rate in operation  
    # looking at the status.state_battery_inout value
    # irritatingly there is no mechanism in the API to do a single set to you have to work out if
    # the direction of the flow and then call the appropriate API 
    def set_manual_flowrate(self, direction, rate, isretry=False):
        path=self.setpoint+direction+"/"+str(rate)
        response = self._post(path)
        return (response.status_code == 201)
    
    def set_discharge(self, rate):
        return self.set_manual_flowrate(SONNEN_DISCHARGE_PATH, rate)
    

    def set_charge(self, rate):
        return self.set_manual_flowrate(SONNEN_CHARGE_PATH, rate)

    # more general purpose endpoints
    def set_configuration(self, name, value):
        # All configurations names and values are hendled as strings, so force that
        payload = {str(name): str(value)}
        return self._put(SONNEN_API_PATH_CONFIGURATIONS, payload)

    def get_powermeter(self):
        return self._get(SONNEN_API_PATH_POWER_METER)
        
    def get_batterysystem(self):
        return self._get(SONNEN_API_PATH_BATTERY_SYSTEM)
        
    def get_inverter(self):
        return self._get(SONNEN_API_PATH_INVERTER)
    
    def get_systemdata(self):
        return self._get(SONNEN_API_PATH_SYSTEM_DATA)

    def get_status(self):
        return self._get(SONNEN_API_PATH_STATUS)
        
    def get_battery(self):
        return self._get(SONNEN_API_PATH_BATTERY)
        
    def get_latest_data(self):
        return self._get(SONNEN_API_PATH_LATEST_DATA)
    
    def get_configurations(self):
        return self._get(SONNEN_API_PATH_CONFIGURATIONS)
    
    def get_configuration(self, name):
        return self._get(SONNEN_API_PATH_CONFIGURATIONS+"/"+name).get(name) 
    

    # these have special handling in some form, for example converting a mode as a number into a string
    def get_current_charge_level(self):
        return self.get_latest_data().get(SONNEN_LATEST_DATA_CHARGE_LEVEL)

    def get_operating_mode(self):
        return self.get_configuration(SONNEN_CONFIGURATION_OPERATING_MODE)
    
    def get_operating_mode_name(self):
        operating_mode_num = self.get_operating_mode()
        return SONNEN_OPERATING_MODES_TO_OPERATING_MODE_NAMES.get(operating_mode_num)
    
    def set_operating_mode(self, operating_mode):
        return self.set_configuration(SONNEN_CONFIGURATION_OPERATING_MODE, operating_mode)
    
    def set_operating_mode_by_name(self, operating_mode_name):
        return self.set_operating_mode(SONNEN_OPERATING_MODE_NAMES_TO_OPERATING_MODES.get(operating_mode_name))
    
    def get_battery_reserve(self):
        return self.get_configuration(SONNEN_CONFIGURATION_BACKUP_RESERVE)
    
    def set_battery_reserve(self, reserve=5):
        reserve = int(reserve)
        if (reserve < 0) or (reserve > 100):
            raise Exception("Reserve must be between 0 and 100, you specified "+reserve)
        return self.set_configuration(SONNEN_CONFIGURATION_BACKUP_RESERVE, reserve)
    
    # set the reserve to the current battery level adjusted by the offset if provided
    # (a positive offset means that the reserve will be set to more than the current level
    # a negative offser means less than the current level)
    # If the new reserve is less than the minimum reserve then use the minimum reserve
    # the reserve will be tested to ensure it's >= 0 or <= 100
    def set_battery_reserve_relative_to_currentCharge(self, offset=0, minimum_reserve=0):
        current_level = self.get_current_charge_level()
        target_level = current_level +offset
        if (target_level <  minimum_reserve):
            target_level = minimum_reserve
        if (target_level < 0) :
            target_level = 0
        elif (target_level > 100):
            target_level = 100
        return self.set_battery_reserve(target_level)
        
    def get_time_of_use_schedule_as_string(self):
        return self.get_configuration(SONNEN_CONFIGURATION_TOU_SCHEDULE)
    
    def get_time_of_use_schedule_as_json_objects(self):
        return json.loads(self.get_configuration(SONNEN_CONFIGURATION_TOU_SCHEDULE))
    
    def get_time_of_use_schedule_as_schedule(self)-> timeofuseschedule:
        current_schedule = self.get_time_of_use_schedule_as_json_objects() 
        return timeofuseschedule.build_from_json(current_schedule)
        
    # In this case the schedule is a array representation of an array of dictionary formatted time of use entries, each entry has a start time and stop time and a threshold_p_max (max grid power for the entire building including charging)
    def set_time_of_use_schedule_from_json_objects(self, schedule):
        return self.set_configuration(SONNEN_CONFIGURATION_TOU_SCHEDULE, json.dumps(schedule))
   