import redis

# Create a Redis connection instance
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)