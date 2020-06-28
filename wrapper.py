import json
import re
from datetime import datetime, timezone, timedelta
import urllib.parse
import time
import typing
from typing import List


from bs4 import BeautifulSoup
import requests

import dataclasses
from dataclasses_json import dataclass_json


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
	# genre: dict
	livers: List[dict]

@dataclass_json
@dataclasses.dataclass
class HoloFormat:
	streamerName: str
	streamerIconUrl: str
	streamerColor: str
	streamUrl: str
	streamStartTime: str
	streamThumbnailUrl: str
	isNowStreaming: bool

@dataclass_json
@dataclasses.dataclass
class CommonScheduleFormat:
	streamerName: str
	streamerIconUrl: str
	streamerColor: str

	streamUrl: str
	title: str
	thumbnail: str
	startTime: str
	endTime: str
	isNowStream: bool

	startEpoch: float
	# endEpoch: float
	org: str


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

		# return result.json()['data']['events']
		# result = wrapper.getIchikaraSchedule()
		streamEvent = []
		for events in result.json()['data']['events']:
			del events['genre']
			streamEvent.append(IchikaraFormat.from_json(json.dumps(events)))
		return streamEvent
	

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
		eventsSchedule = []

		st_name = ''
		st_icon = ''
		st_color = ''
		st_url = ''
		st_time = ''
		st_thum = ''
		st_now = False
		JST = timezone(timedelta(hours=+9), 'JST')

		for container in base_dom_clear:
			# 大まかに区切られたものが入っているので、それをさらに掘り下げる。
			# print(container)
			for container_divs in container.div:
				if container_divs == '\n':
					continue
				if container_divs.find('div', attrs={"class": "navbar navbar-inverse"}) != None:
					# print(container_divs)
					dateJapanese = container_divs.text.replace('\n','').replace("\r", "").replace(" ", '').encode('utf-8').decode('utf-8')
					# print(f'----------[{dateJapanese}]----------')
					dateMD = re.search(r'([0-9]+)/([0-9]+)', dateJapanese)
					streamMan = str(dateMD.group(1))# 06
					streamD = str(dateMD.group(2))# 26
					now = datetime.now(JST).astimezone()
					streamY = now.year
				else:
					for thumneil in container_divs.div:
						# print(thumneil)
						try:
							event = thumneil.a
							if 'red' in str(event.get('style')):
								# print('[Streamming]')
								st_now = True
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
										# print(f'[streamer]: {streamer}')
										st_name = str(streamer)
										# print(f'[streamLink]: {stream_url}')
										st_url = str(stream_url)

										# streamT = reg.group(1)# 11:00
										streamHM = re.match(r'([0-9]+)\:([0-9]+)', str(reg.group(1)))
										# print(streamHM)
										streamH = streamHM.group(1)
										streamM = streamHM.group(2)
										streamEventTime = datetime(int(streamY), int(streamMan), int(streamD), int(streamH), int(streamM)).astimezone()
										# print(f"[streamEventTime]: {streamEventTime.isoformat()}")
										st_time = streamEventTime.isoformat()

										# print(f'date: {reg.group(1)}, who: {reg.group(2)}')
									except Exception as e:
										# print(e)
										try:
											#image
											img = divs.img.get('src')# images
											style = divs.img.get('style')
											if 'mqdefault' in str(img):
												# print(f"[streamThumbnail]: {img}")
												st_thum = img
											# else:
											elif 'https://yt3.ggpht.com' in str(img):
												# print(f"[streamerIcon]: {img}")
												st_icon = img
												# print(str(img_style))
												# vColor = re.match(r"(\#[a-zA-Z0-9]+)", str(img_style))
												# img_style = divs.img.get('style')
												vColor = re.search(r"(\#[a-zA-Z0-9]+)", str(style))
												# print(f'[streamerColor]: {vColor.group(1)}')
												st_color = vColor.group(1)
												sch = HoloFormat(
													streamerName=st_name,
													streamerIconUrl=st_icon,
													streamerColor=st_color,
													streamUrl=st_url,
													streamStartTime=st_time,
													streamThumbnailUrl=st_thum,
													isNowStreaming=st_now
												)
												eventsSchedule.append(sch)
												st_name = ''
												st_icon = ''
												st_color = ''
												st_url = ''
												st_time = ''
												st_thum = ''
												st_now = False
												# print('----------------------------------------------------------------------------------------------------')
												# print(events)
												# sch = HoloFormat()
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
		return eventsSchedule


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
		return result
	

	def getStreamTitleFromURL(self, youtube_stream_url):
		params = {"format": "json", "url": youtube_stream_url}
		url = "https://www.youtube.com/oembed"
		query_string = urllib.parse.urlencode(params)
		url = url + "?" + query_string
		time.sleep(0.2)
		result = requests.get(url)
		# print(result.json())
		if result.status_code == 200:
			return str(result.json()['title'])
		else:
			return ''

		# with urllib.request.urlopen(url) as response:
		# 	response_text = response.read()
		# 	data = json.loads(response_text.decode())
		# 	print(data['title'])

	
	def changeIchikaraFormatToCommon(self, ichikaraSchedule:list) -> list:
		JST = timezone(timedelta(hours=+9), 'JST')

		commonedSchedule = []
		for events in ichikaraSchedule:
			# for isNowStream
			start = datetime.fromisoformat(events.start_date)
			end = datetime.fromisoformat(events.end_date)
			now = datetime.now(JST)
			# endEpoch = end.timestamp()

			if start.timestamp() < now.timestamp() < end.timestamp():
				isStreaming = True
			else:
				isStreaming = False

			# ライバー最初の一人しか取得してない。
			# アプリで複数表示する場合はここを変えればいいんじゃないかな
			ev = CommonScheduleFormat(
				streamerName = events.livers[0]['name'],
				streamerIconUrl = events.livers[0]['avatar'],
				streamerColor = events.livers[0]['color'],
				streamUrl = events.url,
				title = events.name,
				thumbnail = events.thumbnail,
				startTime = events.start_date,
				endTime = events.end_date,
				isNowStream = isStreaming,
				startEpoch = start.timestamp(),
				# endEpoch = endEpoch,
				org = 'ichikara'
			)
			commonedSchedule.append(ev)
		return commonedSchedule


	def changeHoloduleFormatToCommon(self, hololiveSchedule: list) -> list:
		# @dataclasses.dataclass
		# class CommonScheduleFormat:
		# 	streamerName: str
		# 	streamerIconUrl: str
		# 	streamerColor: str

		# 	streamUrl: str
		# 	title: str
		# 	thumbnail: str
		# 	startTime: str
		# 	endTime: str
		# 	isNowStream: bool
		commonSchedule = []
		for events in hololiveSchedule:
			end = datetime.fromisoformat(events.streamStartTime)
			# endEpoch = end.timestamp()
			end += timedelta(hours=2)# hololiveは終了時間書いてないので、適当に2時間にしてる
			start = datetime.fromisoformat(events.streamStartTime)

			ev = CommonScheduleFormat(
				streamerName = events.streamerName,
				streamerIconUrl = events.streamerIconUrl,
				streamerColor = events.streamerColor,
				streamUrl = events.streamUrl,
				title = self.getStreamTitleFromURL(events.streamUrl),
				thumbnail = events.streamThumbnailUrl,
				startTime = events.streamStartTime,
				endTime = end.isoformat(),
				isNowStream = events.isNowStreaming,
				startEpoch = start.timestamp(),
				# endEpoch = endEpoch,
				org = 'hololive'
			)
			commonSchedule.append(ev)
		return commonSchedule


	def integrationCommonSchedules(self, ichikaraCommon:list, hololiveCommon:list):
		# ソートに関して、timestampで比較してしまうと正しい振り分けにならないことを確認。
		# datetimeでそのまま比較できるらしいのでそのようにする

		JST = timezone(timedelta(hours=+9), 'JST')
		masterSchedule = []
		masterSchedule.extend(ichikaraCommon)
		masterSchedule.extend(hololiveCommon)

		sortedSchedule = sorted(masterSchedule, key=lambda x: x.startEpoch)
		# nowEpoch = datetime.now(JST).timestamp()
		now = datetime.now(JST)
		streamSchedule = {
			'past': [],
			'now': [],
			'future': []}
		_id = 0
		for streamEvent in sortedSchedule:
			# if streamEvent
			streamJSON = json.loads(streamEvent.to_json(ensure_ascii=False))
			streamJSON['id'] = _id
			_id += 1

			if '.000' in streamJSON['startTime']:
				streamJSON['startTime'] = str(streamJSON['startTime']).replace('.000', '')

			if '.000' in streamJSON['endTime']:
				streamJSON['endTime'] = str(streamJSON['endTime']).replace('.000', '')

			del streamJSON['startEpoch']
			# del streamJSON['endEpoch']

			if datetime.fromisoformat(streamJSON['startTime']) < now < datetime.fromisoformat(streamJSON['endTime']):
				# 配信中
				streamSchedule['now'].append(streamJSON)

			elif now < datetime.fromisoformat(streamJSON['startTime']):
				# 配信予定
				streamSchedule['future'].append(streamJSON)

			elif datetime.fromisoformat(streamJSON['endTime']) < now:
				# 配信済み
				streamSchedule['past'].append(streamJSON)
			else:
				print(f"[unknown]:\n{streamEvent}")
		return streamSchedule
