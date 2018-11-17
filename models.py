import json
import redis
from datetime import datetime, date
from typing import List
r = redis.Redis(host='redis')


class Product():
    def __init__(self, id: str, brand: str, colors: str, dateAdded: str = None):
        self.id = id
        self.brand = brand
        self.colors = colors
        self.dateAdded = dateAdded

    def as_json(self):
        return json.dumps(self.__dict__)

# TODO: from_json


class RecentProduct():
    def __init__(self, date: str):
        self.date = date

    def set(self, product: Product):
        r.set(f'products:date:{self.date}', product.as_json())

    def get(self):
        return r.get(f'products:date:{self.date}')


class RecentProductsByColor():
    def __init__(self, color: str):
        self.color = color.lower()

    def add(self, product: Product, timestamp: float):
        # TODO: ensure max cap on the list
        r.zadd(f'products:color:{self.color}', {product.as_json(): timestamp})

    def get(self, count=10):
        return r.zrevrange(f'products:color:{self.color}', 0, count)


class BrandCount():
    def __init__(self, date: str):
        self.date = date

    def set(self, brand: str, count: int):
        r.zadd(f'brands:date:{self.date}', {brand: count})

    def get(self):
        return r.zrevrange(f'brands:date:{self.date}', 0, -1, withscores=True)
