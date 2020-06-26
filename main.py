from wrapper import Wrapper
from wrapper import IchikaraFormat
import json


wrapper = Wrapper()
# result = wrapper.getIchikaraSchedule()
# for events in result:
# 	event = IchikaraFormat.from_json(json.dumps(events))
# 	print(event)

result = wrapper.getHololiveSchedule()
# print(result[0])
# for tu in result:
# 	print("\n\n\n\n\n\n\n\n-----------------------------------------")
# 	print('[containaer]\n')
# 	print(tu.encode('utf-8'))
# print(len(result))