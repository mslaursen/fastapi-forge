{% if cookiecutter.use_rabbitmq %}
from {{cookiecutter.project_name}}.services.rabbitmq.rabbitmq_dependencies import QueueConfig
{% endif %}

{% if cookiecutter.use_builtin_auth %}
# Auth
CREATE_TOKEN_EXPIRE_MINUTES = 30
{% endif %}
{% if cookiecutter.use_rabbitmq %}
# RabbitMQ
QUEUE_CONFIGS = [
    QueueConfig(
        exchange_name="demo.exchange",
        queue_name="demo.message.send",
        routing_key="demo.message.send",
    )
]
{% endif %}

