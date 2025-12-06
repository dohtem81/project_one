import pika
import json
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys

from sharedobjects.models import Base, DataRecord

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/project_one_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_rabbitmq_connection():
    """Establish connection to RabbitMQ with retry logic"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            credentials = pika.PlainCredentials(
                os.getenv('RABBITMQ_USER', 'admin'),
                os.getenv('RABBITMQ_PASSWORD', 'admin')
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(parameters)
            print("Successfully connected to RabbitMQ")
            return connection
        except Exception as e:
            print(f"RabbitMQ connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def process_message(ch, method, properties, body):
    """Process incoming message from queue"""
    try:
        # Parse message
        message = json.loads(body)
        print(f"Processing message: {message}")
        
        # Save to database
        db = SessionLocal()
        try:
            record = DataRecord(
                value=message['value'],
                data_type=message.get('data_type'),
                extra_data=message.get('extra_data'),
                timestamp=message.get('timestamp')
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            
            # Broadcast to WebSocket clients
            broadcast_data = {
                "id": record.id,
                "value": record.value,
                "data_type": record.data_type,
                "extra_data": record.extra_data,
                "timestamp": record.timestamp.isoformat()
            }
            
            # This would require async handling - for now just log
            print(f"Data saved: {broadcast_data}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error processing message: {e}")
        # Reject and requeue message
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    """Main consumer loop"""
    print("Starting IoT Consumer Service...")
    
    # Wait for services to be ready
    time.sleep(10)
    
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declare queue (idempotent)
    channel.queue_declare(queue='iot-data', durable=True)
    
    # Set QoS - process one message at a time
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming
    channel.basic_consume(
        queue='iot-data',
        on_message_callback=process_message
    )
    
    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Consumer stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Consumer error: {e}")
        sys.exit(1)
