import gc
import machine
from micropython import const
import network
import time


from MicroWebSrv2 import (GET, POST, MicroWebSrv2, WebRoute)


PUMP_STATUS_PIN = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
# Switching ground
PUMP_CONTROL_PIN = machine.Pin(18, machine.Pin.OUT)
PUMP_CONTROL_PIN.on()

WIFI_CONNECTION_DELAY = const(15)

# In seconds
PUMP_TIME = 0
START_TIME = None
HOUR = 60*60
MINUTE = 60.0


@WebRoute(POST, '/pump-on')
def RequestTestRedirect(microWebSrv2, request):
    global PUMP_TIME
    global START_TIME

    try:
        data = request.GetPostedJSONObject()
        # grab the hours a the end
        btn = data["button"]
        runtime = int(btn.split('-')[-1])
    except Exception as e:
        print("Exception: %s"%(str(e)))
        request.Response.ReturnBadRequest()
        return

    START_TIME = time.time()
    # inverted
    PUMP_CONTROL_PIN.off()
    PUMP_TIME = runtime * HOUR
    
    print("Running pump for %d seconds"%(PUMP_TIME))
    request.Response.ReturnOk()


@WebRoute(POST, '/pump-off')
def RequestTestRedirect(microWebSrv2, request):
    global PUMP_TIME
    global START_TIME

    # inverted
    PUMP_CONTROL_PIN.on()
    PUMP_TIME = 0
    START_TIME = None
    request.Response.ReturnOk('OFF')


@WebRoute(GET, '/pump-status')
def RequestTestRedirect(microWebSrv2, request):
    now = time.time()
    if START_TIME is None:
        remaining = 0
    else:
        remaining = (START_TIME + PUMP_TIME) - now

    if remaining > HOUR:
        hours = int(remaining/HOUR)
        # print("Remaining: %s"%remaining)
        # print("HOUR: %s"%HOUR)
        # print("hours: %s"%(hours*HOUR))
        # print("diff: %s"%(remaining - (hours*HOUR)))
        minutes = (remaining - (hours*HOUR))/MINUTE
        # print("minutes: %s"%minutes)
        time_str = "%d hours and %d minutes remain"%(hours, minutes)
    elif PUMP_TIME > MINUTE:
        time_str = "%d minutes remain"%(round(remaining/MINUTE))
    else:
        time_str = "%d seconds remain"%(remaining)

    running = "OFF"
    if PUMP_STATUS_PIN.value() == 0:
        running = "ON"
    
    status = {
        "running": running,
        "remaining": time_str
    }
    request.Response.ReturnOkJSON(status)


def check_pump_time():
    global PUMP_TIME
    global START_TIME

    if START_TIME is None:
        return

    now = time.time()
    print("Pump elapsed: %s"%(now - START_TIME))
    print("Remaining pump time: %s"%(PUMP_TIME - (now - START_TIME)))
    if now - START_TIME > PUMP_TIME:
        print("Turning Off pump")
        # inverted
        PUMP_CONTROL_PIN.on()
        PUMP_TIME = 0
        START_TIME = None


def loadConfig():
    import config
    return dict(config.config)


def connectToWifi(wifi, config):
    while not wifi.isconnected():
        print("Connecting to WIFI")
        wifi.ifconfig((config["WIFI_IP"], config["WIFI_NETMASK"], config["WIFI_GATEWAY"], config["WIFI_DNS"]))
        wifi.connect(config["WIFI_SSID"], config["WIFI_PASSWD"])
        for x in range(WIFI_CONNECTION_DELAY):
            if wifi.isconnected():
                print(wifi.ifconfig())
                return
            else:
                print(".")
                time.sleep(1)

def main():
    gc.enable()
    gc.collect()
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    config = loadConfig()
    connectToWifi(wifi, config)

    # Wifi is connected. Start the server
    server = MicroWebSrv2()
    server.SetEmbeddedConfig()
    server.RootPath = "/www"
    server.StartManaged()

    # Run loop
    print("###########################################")
    print("########### SERVER RUNNING ################")
    print("###########################################")
    try :
        while server.IsRunning:
            check_pump_time()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("ERROR")
        print(str(e))
        machine.reset()


# start
main()
