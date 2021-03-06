import random
import time
from shadow import customShadowCallback_Delta, customShadowCallback_Update_Desired
from shadow import deviceShadowHandler, cooler, heater
from threading import Timer



# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    if event:
        heater = "ON"
    else:
        heater = "OFF"
    JSONPayload = '{"state":{"desired":{"heater":' + '"' + str(heater) + '"}}}'
    print(JSONPayload)
    deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update_Desired, 5)
    return 