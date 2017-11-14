import os
import asyncio
import json
from sanic import Sanic, response
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

TOPIC = 'json_msgs'

app_dir = os.path.dirname(os.path.realpath(__file__))
index_html_path = os.path.join(app_dir, 'index.html')

loop = asyncio.get_event_loop()

app = Sanic()

app.static('/', index_html_path)

@app.route("/add", methods=['POST'])
async def add(request):
    x = await append_to_topic(request.body)
    return response.json({'offset': x.offset, 'topic': x.topic, 'partition': x.partition})

@app.route("/get_all", methods=['GET'])
async def get_all(request):
    pass

@app.websocket('/feed')
async def feed(request, ws):
    ws_token = request.cookies.get('ws_token')
    consumer = AIOKafkaConsumer(TOPIC, loop=loop, bootstrap_servers='localhost:29092', group_id=ws_token)
    await consumer.start()
    while True:
        try:
            # Consume messages
            async for msg in consumer:
                print("consumed: ", msg.topic, msg.partition, msg.offset,
                      msg.key, msg.value, msg.timestamp)
                print(msg.value)
                await ws.send(msg.value)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()

async def append_to_topic(msg):
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers='localhost:29092')
    await producer.start()
    try:
        x = await producer.send_and_wait(TOPIC, msg)
    finally:
        await producer.stop()
    return x

if __name__ == "__main__":
    server = app.create_server(host="0.0.0.0", port=8000)
    task = asyncio.ensure_future(server)
    loop.run_forever()
