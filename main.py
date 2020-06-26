from wrapper import Wrapper
from wrapper import IchikaraFormat
import json
from flask import Flask, jsonify
import tempfile
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

wrapper = Wrapper()

if os.path.exists('/tmp/vSchedule.json') == False:
	try:
		with open('/tmp/vSchedule.json', 'w') as f:
			ichikaraSchedule = wrapper.getIchikaraSchedule()
			ichikaraCommon = wrapper.changeIchikaraFormatToCommon(ichikaraSchedule)
			hololiveSchedule = wrapper.getHololiveSchedule()
			hololiveCommon = wrapper.changeHoloduleFormatToCommon(hololiveSchedule)

			vSchedule = wrapper.integrationCommonSchedules(hololiveCommon=hololiveCommon, ichikaraCommon=ichikaraCommon)
			with open('/tmp/vSchedule.json', 'w', encoding='utf-8') as f:
				json.dump(vSchedule, f, ensure_ascii=False)
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
	# with tempfile.TemporaryDirectory() as temp_path:
	# write_path = '/tmp' + '/vSchedule.json'
	with open('/tmp/vSchedule.json', 'w', encoding='utf-8') as f:
		json.dump(vSchedule, f, ensure_ascii=False)
	return jsonify({'status': 'ok'}), 200


@app.route('/api/schedule/<time>', methods=['GET'])
def getNowStreaming(time=None):
	with open('/tmp/vSchedule.json', 'r', encoding='utf-8') as f:
		vSchedule = json.loads(f.read())
	if time in ['past', 'now', 'future']:
		return jsonify({time: vSchedule[time]}), 200
	elif time == 'all':
		return jsonify(vSchedule), 200
	else:
		return jsonify({}), 404

if __name__ == '__main__':
	app.run(host='0.0.0.0')