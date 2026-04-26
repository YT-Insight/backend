"""
RabbitMQ publisher for the API service.

Opens a fresh connection per publish call — safe under Django's multi-threaded
WSGI server without requiring a shared connection pool.  The overhead
(~5-15 ms for localhost, ~25-50 ms for a remote broker) is acceptable because
this is called once per analysis submission.

Topology is declared on every publish so the API service is self-healing:
if RabbitMQ restarts and loses transient state, the first publish re-creates
all exchanges and queues.
"""

import json
import logging

import pika
import pika.exceptions
from django.conf import settings

logger = logging.getLogger(__name__)

EXCHANGE = "yt_insight"
DLX = "yt_insight.dlx"


def _get_params() -> pika.URLParameters:
    url = settings.RABBITMQ_URL
    params = pika.URLParameters(url)
    params.heartbeat = 60
    params.blocked_connection_timeout = 300
    params.connection_attempts = 3
    params.retry_delay = 2
    return params


def _declare_topology(ch) -> None:
    """Idempotent: safe to call on every publish."""
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.exchange_declare(exchange=DLX, exchange_type="direct", durable=True)

    ch.queue_declare(queue="dlq", durable=True)
    ch.queue_bind(queue="dlq", exchange=DLX, routing_key="dlq")

    for queue_name in ("analysis.requested", "youtube.data.ready"):
        ch.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": DLX,
                "x-dead-letter-routing-key": "dlq",
            },
        )
        ch.queue_bind(queue=queue_name, exchange=EXCHANGE, routing_key=queue_name)


def publish_analysis_requested(
    analysis_id: str,
    channel_url: str,
    user_id: str,
    max_videos: int = 20,
    max_comments_per_video: int = 300,
) -> None:
    """
    Publish an analysis.requested message to RabbitMQ.

    Raises pika.exceptions.AMQPError (and its subclasses) on connection failure
    so callers can decide whether to roll back the DB write.
    """
    payload = json.dumps(
        {
            "analysis_id": analysis_id,
            "channel_url": channel_url,
            "user_id": user_id,
            "max_videos": max_videos,
            "max_comments_per_video": max_comments_per_video,
        }
    ).encode()

    conn = pika.BlockingConnection(_get_params())
    try:
        ch = conn.channel()
        _declare_topology(ch)
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key="analysis.requested",
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                content_type="application/json",
            ),
        )
        logger.info("Published analysis.requested for analysis %s", analysis_id)
    finally:
        conn.close()
