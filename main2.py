# from urllib.parse import urlencode
#
# import aiohttp
# import asyncio
#
# async def main():
#     query = urlencode({
#         "search_query": "1",
#         "page": 1,
#         "sp": "EgIQAQ%3D%3D",
#         "persist_gl": 1,
#         "gl": "US"
#     })
#     url = "https://www.youtube.com/results" + "?" + query
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#
#             print("Status:", response.status)
#             print("Content-type:", response.headers['content-type'])
#
#             html = await response.text()
#             # page = response.decode('utf_8')
#             page = html
#             ids = []
#             if page[0:29] == '  <!DOCTYPE html><html lang="':
#                 pageSource = page.split()
#                 for index in range(0, len(pageSource) - 1, 1):
#                     element = pageSource[index]
#                     if element[0:15] == 'href="/watch?v=' and len(
#                             'www.youtube.com' + element[6:len(element) - 1]) == 35:
#                         if element[15:len(element) - 1] not in self.ids:
#                             ids += [element[15:len(element) - 1]]
#             else:
#                 pageSource = page.split('":"')
#                 for index in range(0, len(pageSource) - 1, 1):
#                     if pageSource[index][0:9] == '/watch?v=':
#                         id = pageSource[index][9:20]
#                         ids += [id]
#             print(ids)
#
#             print("Body:", html[:15], "...")
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())


import asyncio
from urllib.parse import urlencode
import time
from aiohttp import ClientSession
import aioredis

t0 = time.time()

async def hello(i, url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            # response = await response.read()
            html = await response.text()
            page = html
            ids = []
            if page[0:29] == '  <!DOCTYPE html><html lang="':
                pageSource = page.split()
                for index in range(0, len(pageSource) - 1, 1):
                    element = pageSource[index]
                    if element[0:15] == 'href="/watch?v=' and len(
                            'www.youtube.com' + element[6:len(element) - 1]) == 35:
                        if element[15:len(element) - 1] not in self.ids:
                            ids += [element[15:len(element) - 1]]
            else:
                pageSource = page.split('":"')
                for index in range(0, len(pageSource) - 1, 1):
                    if pageSource[index][0:9] == '/watch?v=':
                        id = pageSource[index][9:20]
                        ids += [id]
            print(ids)
            redis = await aioredis.create_redis_pool(
                'redis://localhost')
            await redis.set(i, ids[0])

def get_first_id(page):
    ids = []
    if page[0:29] == '  <!DOCTYPE html><html lang="':
        pageSource = page.split()
        for index in range(0, len(pageSource) - 1, 1):
            element = pageSource[index]
            if element[0:15] == 'href="/watch?v=' and len(
                    'www.youtube.com' + element[6:len(element) - 1]) == 35:
                if element[15:len(element) - 1] not in self.ids:
                    ids += [element[15:len(element) - 1]]
    else:
        pageSource = page.split('":"')
        for index in range(0, len(pageSource) - 1, 1):
            if pageSource[index][0:9] == '/watch?v=':
                id = pageSource[index][9:20]
                ids += [id]
    return ids[0]

def make_url(search):
    query = urlencode({
                "search_query": search,
                "page": 1,
                "sp": "EgIQAQ%3D%3D",
                "persist_gl": 1,
                "gl": "US"
            })
    url = "https://www.youtube.com/results" + "?" + query
    return url

async def fetch(url, session, redis, i):
    async with session.get(url) as response:
        # delay = response.headers.get("DELAY")
        # date = response.headers.get("DATE")
        html = await response.text()
        vid = get_first_id(html)
        await redis.set(i, vid)
        print(vid)
        return vid
        # print("{}:{} with delay {}".format(date, response.url, delay))
        # return await response.read()



async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)

async def run(r, loop):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        redis = await aioredis.create_redis_pool(
            "redis://localhost", minsize=5, maxsize=100000, loop=loop
        )
        for i in range(r):
            url = make_url(i)
            print(url)
            # pass Semaphore and session to every GET request
            # task = asyncio.ensure_future(bound_fetch(sem, url, session))
            task = asyncio.ensure_future(fetch(url, session, redis, i))
            # task = asyncio.gather(fetch(url, session, redis, i))
            tasks.append(task)

    # return tasks
        responses = asyncio.gather(*tasks)
        await responses
        redis.close()
        await redis.wait_closed()


tasks = []

# for i in range(1000):
#     url = make_url(i)
#     print(url)
#     task = asyncio.ensure_future(hello(i, url))
#     tasks.append(task)
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.wait(tasks))



number = 10
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(number, loop))
# futures = run(number, loop)
# print(type(futures))
# future = asyncio.wait(run(number, loop))

loop.run_until_complete(future)
print("finished at {} sec".format(time.time()-t0,))