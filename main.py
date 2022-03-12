import gc
import machine
from micropython import const
import network
import time


from MicroWebSrv2 import (GET, POST, MicroWebSrv2, WebRoute)


PUMP_STATUS_PIN = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
PUMP_CONTROL_PIN = machine.Pin(18, machine.Pin.OUT)
PUMP_CONTROL_PIN.on()

WIFI_CONNECTION_DELAY = const(15)

# In seconds
PUMP_TIME = 0
START_TIME = None
HOUR = 60*60
MINUTE = 60.0

INDEX_FILE = "/www/index.html"
SCRIPTS_FILE = "/www/scripts.js"
INDEX_MIMETYPE = MicroWebSrv2.GetMimeTypeFromFilename(INDEX_FILE)
SCRIPTS_MIMETYPE = MicroWebSrv2.GetMimeTypeFromFilename(SCRIPTS_FILE)


@WebRoute(POST, '/pump-on')
def RequestTestRedirect(microWebSrv2, request):
    global PUMP_TIME
    global START_TIME

    try:
        data = request.GetPostedJSONObject()
        # grab the hours a the end
        btn = data["button"]
        btn_time = btn.split('-')[-1]
        if btn_time.endswith("min"):
            runtime = float(btn_time[0:-3]) / 60.0
        elif btn_time.endswith("hr"):
            runtime = float(btn_time[0:-2])
        else:
            runtime = float(btn_time)
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
    request.Response.AllowCaching = False
    request.Response.ReturnOkJSON(status)


@WebRoute(GET, '/')
def RequestTestRedirect(microWebSrv2, request):
    request.Response.AllowCaching = False
    # set cache age to 6hrs
    request.Response.SetHeader('Cache-Control', 'public, max-age=21600')
    request.Response.ContentType = INDEX_MIMETYPE
    request.Response.ReturnFile(INDEX_FILE)


@WebRoute(GET, '/scripts.js')
def RequestTestRedirect(microWebSrv2, request):
    request.Response.AllowCaching = False
    # set cache age to 6hrs
    request.Response.SetHeader('Cache-Control', 'public, max-age=21600')
    request.Response.ContentType = SCRIPTS_MIMETYPE
    request.Response.ReturnFile(SCRIPTS_FILE)


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
        if "WIFI_IP" in config:
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
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("ERROR")
        print(str(e))
        machine.reset()


# start
main()
