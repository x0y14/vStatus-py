from wrapper import Wrapper
from wrapper import IchikaraFormat
import json
from flask import Flask, jsonify
import tempfile
import os

app = Flask(__name__)
wrapper = Wrapper()

if os.path.exists('/tmp/vSchedule.json') == False:
	with open('/tmp/vSchedule.json', 'w') as f:
		ichikaraSchedule = wrapper.getIchikaraSchedule()
		ichikaraCommon = wrapper.changeIchikaraFormatToCommon(ichikaraSchedule)
		hololiveSchedule = wrapper.getHololiveSchedule()
		hololiveCommon = wrapper.changeHoloduleFormatToCommon(hololiveSchedule)

		vSchedule = wrapper.integrationCommonSchedules(hololiveCommon=hololiveCommon, ichikaraCommon=ichikaraCommon)
		# with tempfile.TemporaryDirectory() as temp_path:
		# write_path = '/tmp' + '/vSchedule.json'
		with open('/tmp/vSchedule.json', 'w') as f:
			json.dump(vSchedule, f, ensure_ascii=False, encode='utf-8')


@app.route("/api/private/getScheduleData", methods=['GET'])
def getSchedule():
	ichikaraSchedule = wrapper.getIchikaraSchedule()
	ichikaraCommon = wrapper.changeIchikaraFormatToCommon(ichikaraSchedule)
	hololiveSchedule = wrapper.getHololiveSchedule()
	hololiveCommon = wrapper.changeHoloduleFormatToCommon(hololiveSchedule)

	vSchedule = wrapper.integrationCommonSchedules(hololiveCommon=hololiveCommon, ichikaraCommon=ichikaraCommon)
	# with tempfile.TemporaryDirectory() as temp_path:
	# write_path = '/tmp' + '/vSchedule.json'
	with open('/tmp/vSchedule.json', 'w') as f:
		json.dump(vSchedule, f, ensure_ascii=False, encode='utf-8')
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

if __name__ == "__main__":
	app.run()

