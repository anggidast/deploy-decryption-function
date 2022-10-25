import sys
import base64
from google.cloud import pubsub_v1
import json

project_id = 'crm-production-335312'
table_name = ''
topic_sink = ''
encrypted_cols = []
date_cols = []
publisher = pubsub_v1.PublisherClient()

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    payload = base64.b64decode(event['data']).decode('utf-8')
    data = json.loads(payload)
    globals()['table_name'] = data['table_name']
    globals()['topic_sink'] = 'decrypt-passion-sink'

    print('data: %s' % data)
    json_data = {
        "topic": topic_sink,
        "message": {
            "table_name": table_name,
            data['id']: data
        }
    }
    publish(json_data)

# Publishes a message to a Cloud Pub/Sub topic.
def publish(data):
    topic_name = data.get("topic")
    message = data.get("message")
    print('topic_name: %s, message: %s' %(topic_name, message))

    if not topic_name or not message:
        return ('Missing "topic" and/or "message" parameter.', 400)

    print(f'Publishing message to topic {topic_name}')

    # References an existing topic
    topic_path = publisher.topic_path(project_id, topic_name)

    message_json = json.dumps({
        'data': {'message': message},
    })
    message_bytes = message_json.encode('utf-8')

    # Publishes a message
    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
        return 'Message published.'
    except Exception as e:
        print(e)
        return (e, 500)