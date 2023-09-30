from rabbitmq import RabbitMQ
import os
import json
from scraper import Scraper

# Initialize RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
CONSUME_QUEUE_NAME = os.getenv("CONSUME_QUEUE_NAME")
PUBLISH_QUEUE_NAME = os.getenv("PUBLISH_QUEUE_NAME")

def process_message(ch, method, properties, body):
    try:
        # Deserialize the message body
        received_message = json.loads(body.decode('utf-8'))

        print(f"Received message: {received_message}")

        lead_id = received_message['leadId']
        website_url = received_message['websiteUrl']
        
        website_text = Scraper.scrape_website(website_url)
        emails = Scraper.extract_emails(website_text)
        print(f"Found emails: {emails}")

        lead_update_message = {
            'leadId': lead_id,
            'contactEmails': emails,
            'website': website_url  # Optional, can be removed if not needed
        }

        serialized_message = json.dumps(lead_update_message)
        publisher = RabbitMQ(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS)
        publisher.publish_message('lead-details-update', serialized_message)
        publisher.close_connection()
    except Exception as e:
        print(f"Error processing message: {e}")
    finally:
        # Acknowledge the original message
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    print("Starting worker...")
    consumer = RabbitMQ(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS)

    consumer.consume_messages(CONSUME_QUEUE_NAME, process_message)