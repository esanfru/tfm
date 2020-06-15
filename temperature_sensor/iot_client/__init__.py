import greengrasssdk

iot_client = greengrasssdk.client('iot-data')

def get_read_topic(gpio_num, thingName):
    return '/'.join(['gpio', thingName, str(gpio_num), 'read'])

def get_write_topic(gpio_num, thingName):
    return '/'.join(['gpio', thingName, str(gpio_num), 'write'])

def send_message_to_connector(topic, message=''):
    print(f"Topic send {topic} with message {message}")
    iot_client.publish(topic=topic, payload=str(message))

def set_gpio_state(gpio, state, thingName):
    send_message_to_connector(get_write_topic(gpio, thingName), str(state))

def read_gpio_state(gpio, thingName):
    send_message_to_connector(get_read_topic(gpio, thingName))
    return

