import json
import hashlib
from functools import wraps
from inspect import signature
from typing import Callable, Any
from configs import get_redis


def redis_cache(prefix: str, ttl: int = 60):
    """
    Асинхронный декоратор кеша для методов классов.
    Игнорирует self и стабильно сериализует только параметры функции.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            redis = get_redis()

            # Извлекаем имена аргументов функции
            sig = signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            # Убираем self (чтобы не ломал сериализацию)
            params = {k: v for k, v in bound.arguments.items() if k != "self"}

            # Стабильная сериализация аргументов
            def default_serializer(obj):
                if hasattr(obj, "value"):  # Enum
                    return obj.value
                if hasattr(obj, "isoformat"):  # datetime
                    return obj.isoformat()
                if isinstance(obj, (list, tuple, set)):
                    return [default_serializer(i) for i in obj]
                return str(obj)

            key_json = json.dumps(params, sort_keys=True, default=default_serializer)
            cache_key = f"{prefix}:{hashlib.md5(key_json.encode()).hexdigest()}"
            print(cache_key)
            # Проверяем кеш
            cached_value = await redis.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Выполняем и сохраняем
            result = await func(*args, **kwargs)

            # Преобразуем Pydantic модель в dict
            if hasattr(result, "model_dump"):
                result = result.model_dump()

            await redis.set(cache_key, json.dumps(result, default=str), ex=ttl)
            return result

        return wrapper

    return decorator
