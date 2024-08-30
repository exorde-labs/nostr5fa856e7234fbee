import pytz
from pynostr.relay_manager import RelayManager
from pynostr.filters import FiltersList, Filters
from pynostr.event import EventKind
import time
import nest_asyncio
import uuid
import random
import asyncio
import logging
from typing import AsyncGenerator
from datetime import datetime, timedelta
from exorde_data import (
    Item,
    Content,
    CreatedAt,
    Url,
    Domain,
    ExternalId
)
import bech32

# requirements are: pynostr==0.6.2, bech32==1.2.0, nest_asyncio==1.5.6

RANDOM_NUMBER_OF_RELAYS_TO_USE = 1
DEFAULT_OLDNESS_SECONDS = 1000
DEFAULT_MAXIMUM_ITEMS = 30
DEFAULT_MIN_POST_LENGTH = 10
ALL_RELAYS = {
    "wss://relay.nostrdice.com",
    "wss://lunchbox.sandwich.farm",
    "wss://relay.snort.social",
    "wss://relay.current.fyi",
    "wss://nostr.x0f.org",
    "wss://bitcoinmaximalists.online",
    "wss://relay.nostrhub.fr",
    "wss://nostr.wine",
    "wss://bitcoiner.social",
}


def read_parameters(parameters):
    # Check if parameters is not empty or None
    if parameters and isinstance(parameters, dict):
        try:
            max_oldness_seconds = parameters.get("max_oldness_seconds", DEFAULT_OLDNESS_SECONDS)
        except KeyError:
            max_oldness_seconds = DEFAULT_OLDNESS_SECONDS

        try:
            maximum_items_to_collect = parameters.get("maximum_items_to_collect", DEFAULT_MAXIMUM_ITEMS)
        except KeyError:
            maximum_items_to_collect = DEFAULT_MAXIMUM_ITEMS

        try:
            min_post_length = parameters.get("min_post_length", DEFAULT_MIN_POST_LENGTH)
        except KeyError:
            min_post_length = DEFAULT_MIN_POST_LENGTH

    else:
        # Assign default values if parameters is empty or None
        max_oldness_seconds = DEFAULT_OLDNESS_SECONDS
        maximum_items_to_collect = DEFAULT_MAXIMUM_ITEMS
        min_post_length = DEFAULT_MIN_POST_LENGTH

    return max_oldness_seconds, maximum_items_to_collect, min_post_length




def convert_to_datetime_from_timestamp(_timestamp):
    """
    Converts timestamp to datetime object.
    """
    return datetime.fromtimestamp(_timestamp).strftime("%Y-%m-%dT%H:%M:%S.00Z")


def check_for_max_age_with_correct_format(_date, _max_age):
    date_to_check = datetime.strptime(_date, "%Y-%m-%dT%H:%M:%S.00Z")
    now_time = datetime.strptime(datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%dT%H:%M:%S.00Z"),
                                 "%Y-%m-%dT%H:%M:%S.00Z")
    if (now_time - date_to_check).total_seconds() <= _max_age:
        return True
    else:
        return False

def encode_nostr_event(event_id, relays=None, pubkey=None):
    # Prepare the TLV structure
    tlv = []
    
    # Add the event ID (Type 0)
    tlv.append((0, bytes.fromhex(event_id)))
    
    # Optionally add relay information (Type 1)
    if relays:
        for relay in relays:
            tlv.append((1, relay.encode('ascii')))
    
    # Optionally add author public key (Type 2)
    if pubkey:
        tlv.append((2, bytes.fromhex(pubkey)))
    
    # Flatten the TLV into a byte array
    data = bytearray()
    for t, v in tlv:
        data.append(t)
        data.append(len(v))
        data.extend(v)
    
    # Encode using bech32
    hrp = 'nevent'
    return bech32.bech32_encode(hrp, bech32.convertbits(data, 8, 5))


async def parse_nostr():
    relay_manager = RelayManager(timeout=2)
    try:
        logging.basicConfig(level=logging.INFO)
        nest_asyncio.apply()  # allows for nested async loops, essential here
        select_relayed = random.sample(list(ALL_RELAYS), RANDOM_NUMBER_OF_RELAYS_TO_USE)
        for relay in select_relayed:
            logging.info("Adding relay" + relay)
            relay_manager.add_relay(relay)

        # to find a specific post on nostr, we will need to use the id of the post in the following way:
        # filters = FiltersList([Filters(kinds=[EventKind.TEXT_NOTE], limit=[limit], ids=["<id of the post>"])])
        filters = FiltersList(
            [Filters(kinds=[EventKind.TEXT_NOTE], limit=DEFAULT_MAXIMUM_ITEMS * 5)])  # *5 to make sure we get enough items
        subscription_id = uuid.uuid1().hex
        relay_manager.add_subscription_on_all_relays(subscription_id, filters)
        relay_manager.run_sync()

        current_ids = []
        content_checker = []  # some of the content is posted multiple times on different relays at the same time, with different ids
        while relay_manager.message_pool.has_events():
            event_msg = relay_manager.message_pool.get_event()
            date = convert_to_datetime_from_timestamp(event_msg.event.created_at)
            # remove 2 hours from the date to adjust for the time difference between the server and the local time
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.00Z") - timedelta(hours=2)
            # back to  string
            date = date.strftime("%Y-%m-%dT%H:%M:%S.00Z")


            if check_for_max_age_with_correct_format(date, DEFAULT_OLDNESS_SECONDS):
                if event_msg.event.id not in current_ids and event_msg.event.content not in content_checker:  # new item that we can select
                    current_ids.append(event_msg.event.id)
                    # convert the ID to bech32
                    bech32_id = encode_nostr_event(event_id=str(event_msg.event.id), relays=select_relayed)
                    logging.info(f"[NOSTR] POST ID: {bech32_id} - Content: {event_msg.event.content}")
                    content_checker.append(event_msg.event.content)
                    yield Item(
                        content=Content(str(event_msg.event.content)),
                        created_at=CreatedAt(date),
                        url=Url("https://nostr.social/"  + str(bech32_id)),
                        domain=Domain("nostr.social"),
                        external_id=ExternalId(str(bech32_id))
                    )
    except Exception as e:
        logging.exception(f"Error: {str(e)}")
    finally:
        relay_manager.close_all_relay_connections()


async def query(parameters: dict) -> AsyncGenerator[Item, None]:
    yielded_items = 0
    max_oldness_seconds, maximum_items_to_collect, min_post_length = read_parameters(parameters)
    logging.info(f"[nostr.social] - Scraping ideas posted less than {max_oldness_seconds} seconds ago.")

    async for item in parse_nostr():
        yielded_items += 1
        yield item
        logging.info(f"[nostr.social] Found new post :\t posted at {item.created_at}, URL = {item.url}")
        if yielded_items >= maximum_items_to_collect:
            break
