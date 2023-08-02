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
import hashlib
from typing import AsyncGenerator
from datetime import datetime
from exorde_data import (
    Item,
    Content,
    CreatedAt,
    Url,
    Domain,
    ExternalId
)

RANDOM_NUMBER_OF_RELAYS_TO_USE = 10
DEFAULT_OLDNESS_SECONDS = 120
DEFAULT_MAXIMUM_ITEMS = 30
DEFAULT_MIN_POST_LENGTH = 10
ALL_RELAYS = {
    "wss://relay.damus.io",
    "wss://eden.nostr.land",
    "wss://nos.lol",
    "wss://relay.snort.social",
    "wss://relay.current.fyi",
    "wss://brb.io",
    "wss://nostr.orangepill.dev",
    "wss://nostr-pub.wellorder.net",
    "wss://nostr.wine",
    "wss://bitcoiner.social",
    "wss://nostr.oxtr.dev",
    "wss://relay.nostr.bg",
    "wss://nostr.mom",
    "wss://nostr.fmt.wiz.biz",
    "wss://nostr.pub-semisol.dev",
    "wss://nostr.onsats.org",
    "wss://relay.nostr.info",
    "wss://nostr.milou.lol",
    "wss://relay.nostr.band",
    "wss://puravida.nostr.land",
    "wss://offchain.pub",
    "wss://relay.orangepill.dev",
    "wss://no.str.cr",
    "wss://nostr.zebedee.cloud",
    "wss://nostr-relay.wlvs.space",
    "wss://atlas.nostr.land",
    "wss://relay.nostrati.com",
    "wss://relay.nostr.com.au",
    "wss://nostr.inosta.cc",
    "wss://nostr.rocks",
    "wss://relay.shitforce.one",
    "wss://relay.nostrss.re",
    "wss://nostr.sidnlabs.nl",
    "wss://relay.flurs.art",
    "wss://relay.nsecbunker.com",
    "wss://purplepag.es",
    "wss://relay.valera.co",
    "wss://nostr.lu.ke",
    "wss://nostr01.counterclockwise.io",
    "wss://nerostr.xmr.rocks",
    "wss://nostr.1f52b.xyz",
    "wss://nostr.fractalized.net",
    "wss://relay.40two.cloud",
    "wss://nostr.cizmar.net",
    "wss://relay.kisiel.net.pl",
    "wss://nostr.0x50.tech",
    "wss://nostr.superfriends.online",
    "wss://spore.ws",
    "wss://nostr.koutakou.tech",
    "wss://nostr.rikmeijer.nl",
    "wss://relay.kongerik.et",
    "wss://nostr.btcmp.com",
    "wss://nostr.roli.io",
    "wss://relay.guggero.org",
    "wss://relay.wellorder.net",
    "wss://nostr.simplex.icu",
    "wss://relay.coindebit.io",
    "wss://nostr.nicfab.eu",
    "wss://nostr.blockpower.capital",
    "wss://relay.nostr.lighting",
    "wss://nostr.openhoofd.nl",
    "wss://nostr.yuv.al",
    "wss://relay.humanumest.social",
    "wss://nostr.incognito.cat",
    "wss://nostr.portemonero.com",
    "wss://relay.nostr.hach.re",
    "wss://nostr-rs-relay.cryptoassetssubledger.com",
    "wss://relay.primal.net",
    "wss://n0p0.shroomslab.net",
    "wss://nostr.xmr.rocks",
    "wss://nostr.shroomslab.net",
    "wss://nostr.sathoarder.com",
    "wss://nostr.thegrungies.com",
    "wss://nostr.l00p.org",
    "wss://strfry.fractalized.ovh",
    "wss://relay.got-relayed.com",
    "wss://nostr.fractalized.ovh",
    "wss://nostr.zerofiat.world",
    "wss://nostr.bitocial.xyz",
    "wss://nostr.hifish.org",
    "wss://nostr.thank.eu",
    "wss://relay2.nostrchat.io",
    "wss://xmr.usenostr.org",
    "wss://nostr.ingwie.me",
    "wss://relay.ingwie.me",
    "wss://nostr.filmweb.pl",
    "wss://nostr.heavyrubberslave.com",
    "wss://nostr.metamadeenah.com",
    "wss://relay.nostrcheck.me",
    "wss://nostr.cruncher.com",
    "wss://nostr.256k1.dev",
    "wss://nostr.xmr.sh",
    "wss://nostr.itas.li",
    "wss://nostr.data.haus",
    "wss://nostr.glate.ch",
    "wss://nostr.zoz-serv.org",
    "wss://nostr.strits.dk",
    "wss://global-relay.cesc.trade",
    "wss://lnbits.michaelantonfischer.com/nostrrelay/michaelantonf",
    "wss://relay.orangepill.ovh",
    "wss://relay.froth.zone",
    "wss://tmp-relay.cesc.trade",
    "wss://relay.nostrfiles.dev",
    "wss://nostr.bitcoinist.org",
    "wss://nostr.olwe.link",
    "wss://nostr.tchaicap.space",
    "wss://relay.hamnet.io",
    "wss://nostr.petrkr.net/strfry",
    "wss://relay1.nostrchat.io",
    "wss://noster.online",
    "wss://foolay.nostr.moe",
    "wss://nostr.f4255529.shop",
    "wss://nostream.sh4.red",
    "wss://relay.nostrplebs.com",
    "wss://nostr.chatbett.de",
    "wss://nostr.fmar.link",
    "wss://nostr.gleeze.com",
    "wss://nostr.lnbitcoin.cz",
    "wss://nostrua.com",
    "wss://relay.sh4.red",
    "wss://nostr.thedroth.rocks",
    "wss://nostr.rubberdoll.cc",
    "wss://relay.bitcoinbarcelona.xyz",
    "wss://nostr.rbel.co",
    "wss://ithurtswhenip.ee",
    "wss://feeds.nostr.band/nostrhispano",
    "wss://nostr.600.wtf",
    "wss://relay.vanderwarker.family",
    "wss://fiatdenier.nostr1.com",
    "wss://nostrools.nostr1.com",
    "wss://rly.social",
    "wss://fistfistrelay.nostr1.com",
    "wss://zh.nostr1.com",
    "wss://therelayofallrelays.nostr1.com",
    "wss://cloudfodder.nostr1.com",
    "wss://butcher.nostr1.com",
    "wss://wbc.nostr1.com",
    "wss://tictac.nostr1.com",
    "wss://satdow.relaying.io",
    "wss://ryan.nostr1.com",
    "wss://christpill.nostr1.com",
    "wss://nostr.pinkanki.org",
    "wss://pleb.cloud",
    "wss://pater.nostr1.com",
    "wss://relay.toastr.space",
    "wss://relay.lacosanostr.com",
    "wss://dev.nostrplayground.com",
    "wss://nostrue.com",
    "wss://nostr-relay.texashedge.xyz",
    "wss://relay.rip",
    "wss://relay.house",
    "wss://nostr.getgle.org",
    "wss://relay1.nostr.unitedfop.com",
    "wss://nostr.terminus.money",
    "wss://e.nos.lol",
    "wss://relay.bitcoinpark.com",
    "wss://nostr.scaur.nz",
    "wss://nostr.sixteensixtyone.com",
    "wss://relay.hrf.org",
    "wss://nostr.libreleaf.com",
    "wss://nostr.sethforprivacy.com",
    "wss://test.relay.report",
    "wss://relay.bitransfer.org",
    "wss://wc1.current.ninja",
    "wss://relay.bitransfermedia.com",
    "wss://relay.thesimplekid.space",
    "wss://ca.relayable.org",
    "wss://nsc.pleb.cloud",
    "wss://relay.kamp.site",
    "wss://relay.casualcrypto.date",
    "wss://nostr.zbd.gg",
    "wss://nostr.uthark.com",
    "wss://nostr.dakukitsune.ca",
    "wss://relay.wavlake.com",
    "wss://relay.cubanoticias.info",
    "wss://nostr.topeth.info",
    "wss://relay.mostr.pub",
    "wss://lingoh.dev",
    "wss://nostr.geyser.fund",
    "wss://n.xmr.se",
    "wss://relay.nostr.youlot.org",
    "wss://nostr.foundrydigital.com",
    "wss://nostr.fbxl.net",
    "wss://nostr-relay.ktwo.io",
    "wss://connect.chat",
    "wss://nostr.beararmsgroup.org",
    "wss://lnbits.eldamar.icu/nostrrelay/relay",
    "wss://nostr.zenon.info",
    "wss://relay.nostrhackers.online",
    "wss://slick.mjex.me",
    "wss://nostr.sudocarlos.com",
    "wss://nostr.ass.tools",
    "wss://relay.stpaulinternet.net",
    "wss://test.nostr.lc",
    "wss://nproxy.kristapsk.lv",
    "wss://lamp.wtf",
    "wss://nostr.impervious.live",
    "wss://relay.nateflateau.com",
    "wss://nostr.seankibler.com",
    "wss://nostr.dynopool.com",
    "wss://saltivka.org",
    "wss://relay.despera.space",
    "wss://i.relay.boats",
    "wss://nostream.nateflateau.com",
    "wss://zee-relay.fly.dev",
    "wss://relay.chicagoplebs.com",
    "wss://relay.zaptoshi.com",
    "wss://relay.notmandatory.org",
    "wss://la.relayable.org",
    "wss://nostr.frennet.xyz",
    "wss://free.nostr.lc",
    "wss://nostr.tenna.site",
    "wss://nostr.bolt.fun",
    "wss://nostr.irrelevant.mooo.com",
    "wss://relay.utxo.one",
    "wss://nostr.asdf.mx",
    "wss://arc1.arcadelabs.co",
    "wss://nostr-relay.app",
    "wss://nostr.randomdevelopment.biz",
    "wss://nostr.ch3n2k.com",
    "wss://booger.pro",
    "wss://nostr.rocket-tech.net",
    "wss://nostr21.com",
    "wss://nostr.klabo.blog",
    "wss://nostr.hekster.org",
    "wss://relay.protest.net",
    "wss://n.wingu.se",
    "wss://relay.1bps.io",
    "wss://crayon.nostr-demo.relayaas.com",
    "wss://relay.nostrbr.online",
    "wss://relay.break-19.com",
    "wss://anon.computer",
    "wss://nostrrelay.eximpius.xyz",
    "wss://welcome.nostr.wine",
    "wss://nostr-relay.psfoundation.info",
    "wss://relay.f7z.io",
    "wss://relay.nostr.africa",
    "wss://nostr.pjv.me",
    "wss://nostr.azte.co",
    "wss://nostr.maximacitadel.org",
    "wss://nostr.dvdt.dev",
    "wss://nostr.2b9t.xyz",
    "wss://damus.relay.center",
    "wss://denostr.paiya.app",
    "wss://nostr-02.dorafactory.org",
    "wss://relay.keychat.io",
    "wss://offchain.relay.center",
    "wss://nostr-badur.onrender.com",
    "wss://nostr-usa.ka1gbeoa21bnm.us-west-2.cs.amazonlightsail.com",
    "wss://global.relay.red",
    "wss://nostr.xpedite-tech.com",
    "wss://africa.nostr.joburg",
    "wss://nostr-tbd.website",
    "wss://nostr.arguflow.gg",
    "wss://relay.leesalminen.com",
    "wss://nostr.rocketnode.space",
    "wss://nostrpub.yeghro.site",
    "wss://relay.verified-nostr.com",
    "wss://nostr-rs-relay.phamthanh.me",
    "wss://relay.plebz.space",
    "wss://nostr.is-defs.fun",
    "wss://nostr.plebz.space",
    "wss://ts.relays.world",
    "wss://yabu.me",
    "wss://relay.hodl.ar",
    "wss://freerelay.xyz",
    "wss://nostr.dlsouza.lol",
    "wss://relay.greenart7c3.com",
    "wss://relay.beta.fogtype.com",
    "wss://relay.johnnyasantos.com",
    "wss://nostrja-world-relays-test.heguro.com",
    "wss://relay.kiatsu.world",
    "wss://relay1.nostrswap.com",
    "wss://au.relayable.org",
    "wss://nostr.liberty.fans",
    "wss://nostr.dncn.xyz",
    "wss://relay.nostrswap.com",
    "wss://nostrja-kari.heguro.com",
    "wss://nostr.coinfundit.com",
    "wss://nostr-01.yakihonne.com",
    "wss://nostr.kmchu.net",
    "wss://relay.nostrassets.com",
    "wss://relay.nostr.wirednet.jp",
    "wss://relay.austrich.net",
    "wss://nostro.online",
    "wss://nostr.joaorodriguesjr.com",
    "wss://nrelay.c-stellar.net",
    "wss://nostr.cx.ms",
    "wss://jovial-fuchsia-euhyboma.scarab.im",
    "wss://snort.relay.center",
    "wss://nostr.zkid.social",
    "wss://relays.world/nostr",
    "wss://nostr.globals.fans",
    "wss://relay.ohbe.me",
    "wss://jumpy-bamboo-isonychus.scarab.im",
    "wss://nostr-relay.nokotaro.com",
    "wss://nostr.compile-error.net",
    "wss://disrupt-2023.scarab.im",
    "wss://relay.poster.place",
    "wss://nb.relay.center",
    "wss://nostr.danvergara.com",
    "wss://dave.st.germa.in/nostr",
    "wss://relay-verified.deschooling.us",
    "wss://relay.2nodez.com",
    "wss://relay.0xchat.com",
    "wss://klockenga.social",
    "wss://powrelay.xyz",
    "wss://nostr.yonle.lecturify.net",
    "wss://nostr.lecturify.net",
    "wss://bhagos.org",
    "wss://nostr.crypticthreadz.com",
    "wss://lightningrelay.com",
    "wss://at.nostrworks.com",
    "wss://btc.klendazu.com",
    "wss://deschooling.us",
    "wss://knostr.neutrine.com",
    "wss://nostr-1.nbo.angani.co",
    "wss://nostr3.actn.io",
    "wss://nostr.actn.io",
    "wss://nostr.bch.ninja",
    "wss://nostr.bitcoiner.social",
    "wss://nostr.bongbong.com",
    "wss://nostr.cercatrova.me",
    "wss://nostr.corebreach.com",
    "wss://nostr-dev.wellorder.net",
    "wss://nostr.easydns.ca",
    "wss://nostr.einundzwanzig.space",
    "wss://nostrex.fly.dev",
    "wss://nostr.gromeul.eu",
    "wss://nostr.gruntwerk.org",
    "wss://nostr.handyjunky.com",
    "wss://nostr.hugo.md",
    "wss://nostrich.friendship.tw",
    "wss://nostr.kollider.xyz",
    "wss://nostr.massmux.com",
    "wss://nostr.middling.mydns.jp",
    "wss://nostr.mikedilger.com",
    "wss://nostr.nodeofsven.com",
    "wss://nostr.noones.com",
    "wss://nostr-pub1.southflorida.ninja",
    "wss://nostr-relay.bitcoin.ninja",
    "wss://nostr-relay.derekross.me",
    "wss://nostr-relay.lnmarkets.com",
    "wss://nostr-relay.schnitzel.world",
    "wss://nostr.roundrockbitcoiners.com",
    "wss://nostr.satsophone.tk",
    "wss://nostr.screaminglife.io",
    "wss://nostr.shawnyeager.net",
    "wss://nostr.slothy.win",
    "wss://nostr.supremestack.xyz",
    "wss://nostr.swiss-enigma.ch",
    "wss://nostr.uselessshit.co",
    "wss://nostr-verified.wellorder.net",
    "wss://nostr-verif.slothy.win",
    "wss://nostr.vulpem.com",
    "wss://nostr.w3ird.tech",
    "wss://paid.no.str.cr",
    "wss://relay.cryptocculture.com",
    "wss://relay.farscapian.com",
    "wss://relay.minds.com/nostr/v1/ws",
    "wss://relay.n057r.club",
    "wss://relay.nostr.au",
    "wss://relay.nostrich.de",
    "wss://relay.nostrid.com",
    "wss://relay.nostr.nu",
    "wss://relay.nostr.ro",
    "wss://relay.nvote.co",
    "wss://relay.nvote.co:443",
    "wss://relay.oldcity-bitcoiners.info",
    "wss://relay-pub.deschooling.us",
    "wss://relay.sendstr.com",
    "wss://relay.sovereign-stack.org",
    "wss://relay.stoner.com",
    "wss://rsslay.nostr.moe",
    "wss://sg.qemura.xyz",
    "wss://nostr.mining.sc",
    "wss://nostr.cheeserobot.org",
    "wss://soloco.nl"
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


def select_random_relays():
    """
    Selects RANDOM_NUMBER_OF_RELAYS_TO_USE random relays from the list of all relays.
    """
    random_relays = []
    random_relays_index = []
    relay_list = list(ALL_RELAYS)
    first_choice = random.randint(0, 30)
    random_relays.append(relay_list[first_choice])
    random_relays_index.append(first_choice)
    i = 1
    while i < RANDOM_NUMBER_OF_RELAYS_TO_USE:
        random_index = random.randint(0, len(relay_list))
        if random_index not in random_relays_index:
            i += 1
            random_relays.append(relay_list[random_index])
            random_relays_index.append(random_index)

    return random_relays, random_relays_index


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

def generate_fixed_length_hash(input_string, hash_length=32):
    hash_object = hashlib.sha256()  # You can choose a different hash algorithm if desired
    hash_object.update(input_string.encode('utf-8'))
    hash_value = hash_object.digest()[:hash_length]
    hex_hash = hash_value.hex()
    return hex_hash

async def parse_nostr():
    logging.basicConfig(level=logging.INFO)
    nest_asyncio.apply()  # allows for nested async loops, essential here
    relay_manager = RelayManager(timeout=2)
    select_relays, relay_indexes = select_random_relays()


    for relay in select_relays:
        logging.info("[Nostr] Adding relay" + relay)
        try:
            relay_manager.add_relay(relay)
        except Exception as e:
            logging.info(f"[Nostr] Relay Error {e}")


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
        if check_for_max_age_with_correct_format(date, DEFAULT_OLDNESS_SECONDS):
            if event_msg.event.id not in current_ids and event_msg.event.content not in content_checker:  # new item that we can select
                current_ids.append(event_msg.event.id)
                content_checker.append(event_msg.event.content)
                index_string = ""
                for index in relay_indexes:
                    index_string += str(index) + "/"
                external_id_str = index_string + str(event_msg.event.id)
                content_hex_hash = generate_fixed_length_hash(event_msg.event.content)
                forged_URL = "https://nostr/" + content_hex_hash
                yield Item(
                    content=Content(event_msg.event.content),
                    created_at=CreatedAt(date),
                    # url=Url("https://nostr/" + index_string + str(event_msg.event.id)),
                    url = forged_URL,
                    domain=Domain("nostr.social"),
                    external_id=ExternalId(external_id_str),
                )

    relay_manager.close_all_relay_connections()


async def query(parameters: dict) -> AsyncGenerator[Item, None]:
    yielded_items = 0
    max_oldness_seconds, maximum_items_to_collect, min_post_length = read_parameters(parameters)
    logging.info(f"[nostr.social] - Scraping ideas posted less than {max_oldness_seconds} seconds ago.")

    async for item in parse_nostr():
        yielded_items += 1
        yield item
        logging.info(f"[nostr.social] Found new post :\t posted at {item.created_at}, URL = {item.url}, Id = {item.external_id}")
        if yielded_items >= maximum_items_to_collect:
            break
