import requests
import json
import re

from bs4 import BeautifulSoup

import typing
from typing import List

import dataclasses
from dataclasses_json import dataclass_json

from pprint import pprint

from datetime import datetime, timezone


@dataclass_json
@dataclasses.dataclass
class IchikaraFormat:
	id: int
	name: str
	description: str
	public: int
	url: str
	thumbnail: str
	start_date: str
	end_date: str
	recommend: bool
	genre: dict
	livers: List[dict]


class Wrapper:
	def __init__(self):
		self.holo_schedule_url = "https://schedule.hololive.tv"
		self.ichikara_schedule_url = "https://api.itsukaralink.jp/v1.2/events.json"
	

	def getIchikaraSchedule(self) -> list:
		result = requests.get(url=self.ichikara_schedule_url)
		if result.status_code != 200:
			raise Exception("request status is not 200")

		if result.json().get("data") == None:
			raise Exception("return json does not have key of data")
		if result.json()['data'].get("events") == None:
				raise Exception("return json does not have key of events")

		return result.json()['data']['events']
	

	def _holoParse(self, mainDOM):
		# print(mainDOM.div.div.div)
		containers = mainDOM.div.div.div.div
		contList = []
		for cont in containers:
			try:
				if cont.strip() == '':
					continue
			except:
				pass

			if (cont == '\n') or (cont == ''):
				continue
			else:
				contList.append(cont)
		# print(contList)
		if len(contList) > 1:
			raise Exception("so many data, check dom")
		base_dom = contList[0]
		base_dom_clear = []

		for container in base_dom:
			try:
				if container.strip() == '':
					continue
			except:
				base_dom_clear.append(container)

		# we have containers
		# next step, container kaiseki
		events = []


		for container in base_dom_clear:
			# 大まかに区切られたものが入っているので、それをさらに掘り下げる。
			# print(container)
			for container_divs in container.div:
				if container_divs == '\n':
					continue
				if container_divs.find('div', attrs={"class": "navbar navbar-inverse"}) != None:
					# print(container_divs)
					dateJapanese = container_divs.text.replace('\n','').replace("\r", "").replace(" ", '').encode('utf-8').decode('utf-8')
					print(f'----------[{dateJapanese}]----------')
					dateMD = re.search(r'([0-9]+)/([0-9]+)', dateJapanese)
					streamMan = str(dateMD.group(1))# 06
					streamD = str(dateMD.group(2))# 26
					now = datetime.now().astimezone()
					streamY = now.year
# sch = datetime(now.year, int('06'), int('25'), int('00'), int('00')).astimezone()
				# print('\n\n\n-----[container]-----')
				else:
					for thumneil in container_divs.div:
						# print(thumneil)
						try:
							event = thumneil.a
							if 'red' in str(event.get('style')):
								print('[Streamming]')
							stream_url = event.get("href")
							# print(f'[streamLink]: {stream_url}')
							# event = thumneil.a
							for divs in event.div.div:
								if divs == "\n":
									# trash
									# pass
									continue
								else:
									# print('========[divs]========')
									# print(divs)
									try:
										dateAndName = divs.div.text.replace('\n','').replace("\r", "").replace(" ", '').encode('utf-8').decode('utf-8')
										# print(dateAndName)
										reg = re.match(r'([0-9]+\:[0-9]+)([a-zA-Zぁ-龥]+)', dateAndName)
										streamer = reg.group(2)# 常闇トワ
										print(f'[streamer]: {streamer}')
										print(f'[streamLink]: {stream_url}')

										# streamT = reg.group(1)# 11:00
										streamHM = re.match(r'([0-9]+)\:([0-9]+)', str(reg.group(1)))
										# print(streamHM)
										streamH = streamHM.group(1)
										streamM = streamHM.group(2)
										streamEventTime = datetime(int(streamY), int(streamMan), int(streamD), int(streamH), int(streamM)).astimezone()
										print(f"[streamEventTime]: {streamEventTime.isoformat()}")

										# print(f'date: {reg.group(1)}, who: {reg.group(2)}')
									except Exception as e:
										# print(e)
										try:
											#image
											img = divs.img.get('src')# images
											style = divs.img.get('style')
											if 'mqdefault' in str(img):
												print(f"[streamThumbnail]: {img}")
											# else:
											elif 'https://yt3.ggpht.com' in str(img):
												print(f"[streamerIcon]: {img}")
												# print(str(img_style))
												# vColor = re.match(r"(\#[a-zA-Z0-9]+)", str(img_style))
												# img_style = divs.img.get('style')
												vColor = re.search(r"(\#[a-zA-Z0-9]+)", str(style))
												print(f'[streamerColor]: {vColor.group(1)}')
												print('----------------------------------------------------------------------------------------------------')
											else:
												print(img)
										except Exception as e:
											# print(e)
											pass

							# containerもち、正常
						except Exception as e:
							# print(e)
							pass
							# print(thumneil)
							# コンテナーがない、ゴミ

		
		return base_dom_clear


	def getHololiveSchedule(self):
		result = requests.get(url=self.holo_schedule_url)
		if result.status_code != 200:
			raise Exception("request status is not 200")
		soup = BeautifulSoup(result.content, features="html.parser", from_encoding='utf-8')

		mainDOM = None

		# get div.holodule
		div_holodules = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['holodule'])
		for div_holos in div_holodules:
			if div_holos.find_all('ul', attrs={"class": 'drawer-menu'}) != []:
				continue
			elif div_holos.find_all('a', href="https://schedule.hololive.tv/simple") != []:
				continue
			else:
				mainDOM = div_holos

		if mainDOM == None:
			raise Exception("dom parse error")

		result = self._holoParse(mainDOM)

		# containers = mainDOM.div.div.div.div
		# contList = []
		# for cont in containers:
		# 	if (cont == '\n') or (cont == ''):
		# 		continue
		# 	else:
		# 		contList.append(cont)
		# return contList
		return result