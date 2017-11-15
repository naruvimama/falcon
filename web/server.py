import os
import asyncio
import json
import time
from sanic import Sanic, response
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer, TopicPartition

TOPIC = 'json_msgs'

KAFKA_BOOTSTRAP_SERVERS = 'localhost:29092'

app_dir = os.path.dirname(os.path.realpath(__file__))
index_html_path = os.path.join(app_dir, 'index.html')

loop = asyncio.get_event_loop()

app = Sanic()

@app.route("/add", methods=['POST'])
async def add(request):
    x = await append_to_topic(request.body)
    return response.json({'offset': x.offset, 'topic': x.topic, 'partition': x.partition})


@app.route("/get_all", methods=['GET'])
async def get_all(request):
    offset = int(request.args.get('offset', 0))
    limit  = int(request.args.get('limit', 1))
    tp = TopicPartition(TOPIC, 0)
    async def stream_from_kafka(response):
        consumer = AIOKafkaConsumer(TOPIC, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        await consumer.start()
        consumer.seek(tp, offset)

        count = 0
        async for msg in consumer:
            response.write(msg.value.decode('utf-8') + "\n")
            count += 1
            if count>=limit:
                return True

    return response.stream(stream_from_kafka)


@app.websocket('/feed')
async def feed(request, ws):
    ws_token = request.cookies.get('ws_token')
    consumer = AIOKafkaConsumer(TOPIC, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id=ws_token)
    await consumer.start()
    while True:
        try:
            # Consume messages
            async for msg in consumer:
                await ws.send(msg.value.decode('utf-8'))
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()


app.static('/', index_html_path)


async def append_to_topic(msg):
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
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
