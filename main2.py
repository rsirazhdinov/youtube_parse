import asyncio
import time
from urllib.parse import urlencode

import aioredis
from aiohttp import ClientSession

t0 = time.time()


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
	async with session.get(url, timeout=None) as response:
		html = await response.text()
		vid = get_first_id(html)
		await redis.set(i, vid)
		print(vid)
		return vid


async def run(r, loop):
	tasks = []
	async with ClientSession() as session:
		redis = await aioredis.create_redis_pool(
			"redis://localhost", minsize=5, maxsize=10000, loop=loop
		)
		for i in range(r):
			url = make_url(i)
			print(url)
			task = asyncio.ensure_future(fetch(url, session, redis, i))
			tasks.append(task)

		responses = asyncio.gather(*tasks)
		await responses
		redis.close()
		await redis.wait_closed()


number = 100000
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(number, loop))
loop.run_until_complete(future)

print("finished at {} sec".format(time.time() - t0, ))
