from nostr5fa856e7234fbee import query
from exorde_data.models import Item
import logging
import pytest


@pytest.mark.asyncio


async def test_query():
    params = {
        "max_oldness_seconds": 120,
        "maximum_items_to_collect": 10,
        "min_post_length": 10
    }
    try:
        async for item in query(params):
            assert isinstance(item, Item)
            logging.info("Post Link: " + item.url)
            logging.info("Date of Post: " + item.created_at)
            logging.info("Post Content: " + item.content)
    except ValueError as e:
        logging.exception(f"Error: {str(e)}")



import asyncio
asyncio.run(test_query())

