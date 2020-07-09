import logging
import paho.mqtt.publish as publish

log = logging.getLogger('MPP-Solar')


class influx_mqtt():
    def __init__(self, *args, **kwargs) -> None:
        log.info('Using output processor: influx_mqtt')
        log.debug(f'processor.influx_mqtt __init__ kwargs {kwargs}')
        data = kwargs['results']
        tag = kwargs['tag']
        mqtt_broker = kwargs['mqtt_broker']
        if data is None:
            return

        # Build array of Influx Line Protocol messages
        msgs = []
        # Loop through responses
        for key in data:
            value = data[key][0]
            unit = data[key][1]
            # Message format is: tag, tag,setting=total_ac_output_apparent_power value=1577.0,unit="VA"
            msg = {'topic': tag, 'payload': f'{tag},setting={key} value={value},unit={unit}'}
            msgs.append(msg)
        publish.multiple(msgs, hostname=mqtt_broker)
