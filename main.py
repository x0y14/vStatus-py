from wrapper import Wrapper
from wrapper import IchikaraFormat
import json
from pprint import pprint


wrapper = Wrapper()

ichikaraSchedule = wrapper.getIchikaraSchedule()
ichikaraCommon = wrapper.changeIchikaraFormatToCommon(ichikaraSchedule)
hololiveSchedule = wrapper.getHololiveSchedule()
hololiveCommon = wrapper.changeHoloduleFormatToCommon(hololiveSchedule)

schedule = wrapper.integrationCommonSchedules(hololiveCommon=hololiveCommon, ichikaraCommon=ichikaraCommon)
pprint(schedule)