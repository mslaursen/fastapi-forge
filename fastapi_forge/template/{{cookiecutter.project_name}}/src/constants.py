{% if cookiecutter.use_builtin_auth %}
# Auth
CREATE_TOKEN_EXPIRE_MINUTES = {{ cookiecutter.builtin_jwt_token_expire }}
{% endif %}
