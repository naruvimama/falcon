With Docker installed

1. docker-compose build
2. docker-compose up

Visit the page at http://localhost:8000

The textbox takes a json or any text and sends it to a kafka topic ('json_msgs')

In the current configuration kafka buffers the incomming data so is not immediately visible to the consumers.

Each consumer sending messages through websockets is of an independent consumer group, 
and can potentially pick up from where they left. Rewind by offset or timestamp if necessary.

Since Kafka is persistant all the json objects stored can be fetched by seeking to the start.
A seperate database wouldn't be necessary.


To fetch all the items

[http://localhost:8000/get_all?offset=0&limit=1]
