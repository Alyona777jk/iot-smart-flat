import time
import json
import ssl
import sys
import math
import argparse
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

parser = argparse.ArgumentParser(description="IoT Flat Simulator")
parser.add_argument("--scenario", type=str, choices=["normal", "overheat", "motion", "nomotion"], default="normal", help="Trigger specific scenario")
args = parser.parse_args()

BROKER = "mosquitto"
PORT = 8883
CA_CERT = "/app/certs/ca.crt"

def on_connect_actuator(client, userdata, flags, reason_code, properties=None):
    print(f"[Actuator] Connected with code {reason_code}")
    client.subscribe("flat/+/+/set")

def on_message_actuator(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        print(f"[Actuator Received] {topic} -> {payload}")

        state_topic = topic.replace("/set", "/state")
        client.publish(state_topic, json.dumps(payload), qos=1, retain=True)
    except Exception as e:
        print(f"Error handling message: {e}")

def main():
    sensor_cli = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="Python_Sensors")
    sensor_cli.username_pw_set("sensor_user", "sensor_pass_123")
    sensor_cli.tls_set(ca_certs=CA_CERT, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
    sensor_cli.tls_insecure_set(True)
    sensor_cli.will_set("flat/hall/sensor/status", payload="offline", qos=1, retain=True)

    actuator_cli = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="Python_Actuators")
    actuator_cli.username_pw_set("actuator_user", "actuator_pass_123")
    actuator_cli.tls_set(ca_certs=CA_CERT, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
    actuator_cli.tls_insecure_set(True)
    actuator_cli.on_connect = on_connect_actuator
    actuator_cli.on_message = on_message_actuator
    actuator_cli.will_set("flat/room1/light/status", payload="offline", qos=1, retain=True)

    sensor_cli.connect(BROKER, PORT)
    actuator_cli.connect(BROKER, PORT)

    sensor_cli.loop_start()
    actuator_cli.loop_start()

    sensor_cli.publish("flat/hall/sensor/status", "online", qos=1, retain=True)
    actuator_cli.publish("flat/room1/light/status", "online", qos=1, retain=True)

    step = 0
    while True:
        ts = int(time.time())
        step += 1

        temp = round(21.0 + 1.5 * math.sin(step / 10.0), 1)
        humidity = round(45.0 + 3.0 * math.cos(step / 10.0), 1)
        lux = 40 if args.scenario == "motion" else 150
        motion = "ON" if args.scenario in ["motion"] or (step % 6 == 0 and args.scenario != "nomotion") else "OFF"

        power = 2800.0 if args.scenario == "overheat" else round(1200.0 + 300.0 * math.sin(step / 5.0), 1)

        sensor_cli.publish("flat/room1/environment/telemetry", json.dumps({"temp": temp, "humidity": humidity, "ts": ts}), qos=0)
        sensor_cli.publish("flat/room1/lux/telemetry", json.dumps({"value": lux, "unit": "lx", "ts": ts}), qos=0)
        sensor_cli.publish("flat/room1/motion/telemetry", json.dumps({"state": motion, "ts": ts}), qos=0)
        sensor_cli.publish("flat/main/power/telemetry", json.dumps({"value": power, "unit": "W", "ts": ts}), qos=0)

        print(f"[Telemetry Sent] Temp={temp}C, Lux={lux}lx, Motion={motion}, Power={power}W")
        time.sleep(5)

if __name__ == "__main__":
    main()
