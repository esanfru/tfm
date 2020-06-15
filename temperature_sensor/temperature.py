import random
import time
import json
from shadow import customShadowCallback_Delta, customShadowCallback_Update_Desired
from shadow import deviceShadowHandler 
from iot_client import send_message_to_connector, set_gpio_state, read_gpio_state
from threading import Timer

choices = [-0.5, -0.25, 0, 0.25, 0.5]
weights = [10,10,20,30,30]
cooler = False
heater = False
temperature = 25
ref_temperature = 27

# Custom Shadow callback for updating the reported state in shadow
def customShadowCallback_Get(payload, responseStatus, token):
    global heater
    global cooler
    global temperature
    global ref_temperature
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print("Get request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~ Shadow Update Accepted ~~~~~~~~~~~~~")
        print("Get request with token: " + token + " accepted!")
        for key, value in payloadDict["state"]["reported"].items():
            print(f"{key}: {value}")
            if key == "temperature":
                print(f"Temperature: {value}")
                #temperature = float(value)
            if key == "ref_temperature":
                print(f"Reference temperature: {value}")
                ref_temperature = float(value)
            if key == "heater":
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                print("Heater")
                if value == "ON":
                    heater = True
                else:
                    heater = False
                print(heater)
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            
            if key == "cooler":
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                print("Cooler")
                if value == "ON":
                    cooler = True
                else:
                    cooler = False
                    print(cooler)
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def heater_cooler_checker():
    global temperature
    global ref_temperature
    global weights
    global heater
    global cooler
    thingName = "tfm_Core"
    thingName_cooler = "cooler"
    thingName_heater = "heater"
    cooler_gpio = 21
    heater_gpio = 26

    print(f"Weights:{weights}")
    print(f"Cooler: {str(cooler)}")
    print(f"Heater: {str(heater)}")

    if temperature >= ref_temperature + 2:
        print("Cooler ON")
        if not cooler:
            set_gpio_state(cooler_gpio, 1, thingName)
            
        if heater:
            set_gpio_state(heater_gpio, 0, thingName)
        weights = [50,30,10,10,0]

    elif temperature <= ref_temperature - 2:
        print("Heater ON")

        if not heater:
            set_gpio_state(heater_gpio, 1, thingName)

        
        if cooler:
            set_gpio_state(cooler_gpio, 0, thingName)
        weights = [0,10,10,30,50]
        
    elif temperature >= ref_temperature + 1:
        print("Cooler ON 1/2")
        if not cooler:
            set_gpio_state(cooler_gpio, 1, thingName)
            
        if heater:
            set_gpio_state(heater_gpio, 0, thingName)
        weights = [30,50,10,10,0]

    elif temperature <= ref_temperature - 1:
        print("Heater ON 1/2")

        if not heater:
            set_gpio_state(heater_gpio, 1, thingName)

        
        if cooler:
            set_gpio_state(cooler_gpio, 0, thingName)
        weights = [0,10,10,50,30]
        
    elif temperature >= ref_temperature - 0.25 and temperature <= ref_temperature + 0.25:
        print("Reference temperature reached")
        weights = [10,20,40,20,10]
        
    else:
        if cooler:
            print("Cooler OFF")
            set_gpio_state(cooler_gpio, 0, thingName)
            weights = [10,30,40,20,0]

        if heater:
            print("Heater OFF")
            set_gpio_state(heater_gpio, 0, thingName)
            weights = [0,20,40,30,10]

    read_gpio_state(cooler_gpio, thingName_cooler)
    read_gpio_state(heater_gpio, thingName_heater)

def temperature_checker():
    global temperature
    global choices
    global weights
    """
    Simulates a read of temperature sensor GPIOs
    """
    temperature += random.choices(choices, weights=weights, k=1)[0]
    heater_cooler_checker()
    JSONPayload = '{"state":{"desired":{"temperature":' + '"' + str(temperature) + '"}}}'
    print(JSONPayload)
    deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update_Desired, 5)
    deviceShadowHandler.shadowGet(customShadowCallback_Get, 5)
    Timer(10, temperature_checker).start()


# Listen on deltas - customShadowCallback_Delta will be called when a shadow delta message is received
deviceShadowHandler.shadowRegisterDeltaCallback(customShadowCallback_Delta)
temperature_checker()



# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    global ref_temperature
    print(f"Event: {event}")
    print(f"Context: {context}")
    if "ref_temperature" not in event:
        print("Bad format")
        return 
    ref_temperature = event["ref_temperature"]
    heater_cooler_checker()
    JSONPayload = '{"state":{"desired":{"ref_temperature":' + '"' + str(ref_temperature) + '"}}}'
    print(JSONPayload)
    deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update_Desired, 5)
    send_message_to_connector("temperature/reference/state", f"Reference temperature updated to {ref_temperature}")
    return 