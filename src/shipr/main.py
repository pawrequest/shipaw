import asyncio
from pprint import pprint

from apc.available_services.avail_funcs import make_avail_serv_dict, do_request
from apc.available_services.avail_request import dummy_avail_request


async def main():
    dummy_order = await dummy_avail_request()
    req_dict = make_avail_serv_dict(dummy_order)
    response = await do_request(req_dict)
    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())

