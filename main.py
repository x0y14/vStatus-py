from wrapper import Wrapper
from wrapper import IchikaraFormat
import json
from flask import Flask, jsonify, request
import tempfile
import os
from datetime import datetime, timedelta, timezone


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

wrapper = Wrapper()
JST = timezone(timedelta(hours=+9), 'JST')


if os.path.exists('/tmp/vSchedule.json') == False:
	try:
		ichikaraSchedule = wrapper.getIchikaraSchedule()
		ichikaraCommon = wrapper.changeIchikaraFormatToCommon(ichikaraSchedule)
		hololiveSchedule = wrapper.getHololiveSchedule()
		hololiveCommon = wrapper.changeHoloduleFormatToCommon(hololiveSchedule)

		vSchedule = wrapper.integrationCommonSchedules(hololiveCommon=hololiveCommon, ichikaraCommon=ichikaraCommon)
		vSchedule['lastUpdate'] = datetime.now(JST).isoformat()
		try:
			with open('/tmp/vSchedule.json', 'w') as f:
				json.dump(vSchedule, f, ensure_ascii=False)
		except Exception as e:
			print(e)

	except Exception as e:
		print(e)


@app.route('/')
def index():
	return jsonify({'version': 'v0.1'}), 200


@app.route("/api/private/getScheduleData", methods=['GET'])
def getSchedule():
	ichikaraSchedule = wrapper.getIchikaraSchedule()
	ichikaraCommon = wrapper.changeIchikaraFormatToCommon(ichikaraSchedule)
	hololiveSchedule = wrapper.getHololiveSchedule()
	hololiveCommon = wrapper.changeHoloduleFormatToCommon(hololiveSchedule)

	vSchedule = wrapper.integrationCommonSchedules(hololiveCommon=hololiveCommon, ichikaraCommon=ichikaraCommon)
	vSchedule['lastUpdate'] = datetime.now(JST).isoformat()

	# js = json.loads(vSchedule)

	try:
		with open('/tmp/vSchedule.json', 'w', encoding='utf-8') as f:
			json.dump(vSchedule, f, ensure_ascii=False)
	except Exception as e:
		print(e)
	return jsonify({'status': 'ok'}), 200


@app.route('/api/schedule/<time>', methods=['GET'])
def getNowStreaming(time=None):
	try:
		with open('/tmp/vSchedule.json', 'r', encoding='utf-8') as f:
		# json_lines = [ json.loads(s) for s in responses if s != "" ]
			vSchedule = json.loads(f.read())
	except Exception as e:
		return jsonify({'err': str(e)}), 500

	if time in ['past', 'now', 'future']:
		if request.args.get('count') != None:
			try:
				count = int(request.args.get('count'))
			except:
				return jsonify((vSchedule[time])), 200

			return jsonify((vSchedule[time][:count])), 200
		else:
			return jsonify((vSchedule[time])), 200
	elif time == 'all':
		return jsonify((vSchedule)), 200
	else:
		return jsonify({}), 404

@app.route('/api/lastUpdate', methods=['GET'])
def getLastUpdate():
	try:
		with open('/tmp/vSchedule.json', 'r', encoding='utf-8') as f:
			vSchedule = json.loads(f.read())
	except Exception as e:
		return jsonify({'err': str(e)}), 500
	
	return jsonify({'lastUpdate': vSchedule['lastUpdate']}), 200

if __name__ == '__main__':
	app.run()