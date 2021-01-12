# -*- coding: utf-8 -*-
#!/usr/bin/env python
import json
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# options: local || remote
environment = 'local'
# options: c || f
temp_unit = 'c'

# https://docs.google.com/document/d/15ijz94dXJ-YAZLi9iZ_RaBwrZ4KtYeCy08goGBwnbCU/edit
aqi_base_url = 'https://www.purpleair.com/json?show='
# get your PurpleAir Station ID from this list -> https://www.purpleair.com/json
purple_air_station_id = 'find_a_station_id'
full_aqi_url = aqi_base_url + purple_air_station_id

# get your LaMetric Time api_key here -> https://developer.lametric.com/user/devices
lametric_access_token = 'your_api_key_here'
# lametric_basic_auth = 'placeholder'

remote_lametric_base_url = 'https://developer.lametric.com/api/v1/dev/widget/update/'
local_lametric_base_url = 'https://192.168.1.182:4343/api/v1/devices/widget/update/'
lametric_app_id = 'com.lametric.14aaaa95b110cd2864a51f51f094046d/'
lametric_app_version = '1'

first_frame = json.loads('{"text":"PURPLEAIR","icon":"39915","index":0,"duration":1}')
lametric_frames_list = []
lametric_frames_list.append(first_frame)
lametric_frames_dict = {}

def fetch_from_purpleair_and_push_to_lametric():
	def fetch_from_purpleair():
		try:
			aqi_headers = {"Cache-Control":"no-cache"}
			aqi_req = requests.get(full_aqi_url, headers=aqi_headers)
			aqi_dict = json.loads(aqi_req.text)
			print(json.dumps(aqi_dict))
			build_lametric_frames(aqi_dict)
		except requests.exceptions.Timeout as e:
			# timeout
			print(e)
		except requests.exceptions.ConnectionError as e:
			# connection error
			print(e)
		except requests.exceptions.RequestException as e:
			# error
			print(e)

	def build_lametric_frames(sensors):
		sensors = sensors['results'][0]
		for sensor in sensors.keys():
			if sensor == 'PM2_5Value':
				pm25 = sensors[sensor]
				frame_item = {"text": pm25 + " ug/m3","icon":"a38873","index":1}
				lametric_frames_list.append(frame_item)
			elif sensor == 'temp_f':
				deg = u'\xb0'
				icon = "a37978"
				temp = sensors[sensor]
				if temp_unit == 'c':
					temp = (int(temp) - 32) * (5 / 9)
					temp = str(temp)
					icon = "a2422"
				frame_item = {"text": temp + deg + temp_unit,"icon": icon,"index":2,"duration":1}
				lametric_frames_list.append(frame_item)
			elif sensor == 'humidity':
				humid = sensors[sensor]
				frame_item = {"text": humid + "% RH","icon":"a2423","index":3,"duration":1}
				lametric_frames_list.append(frame_item)
			elif sensor == 'pressure':
				pressure = sensors[sensor]
				frame_item = {"text": pressure + " mbar","icon":"a39912","index":5,"duration":1}
				lametric_frames_list.append(frame_item)
			else:
				print("[unknown key] " + sensor + ": " + str(sensors[sensor]))

	def push_to_lametric():
		lametric_frames_dict['frames'] = sorted(lametric_frames_list, key = lambda i: i['index'])
		print(json.dumps(lametric_frames_dict))
		lametric_payload = json.dumps(lametric_frames_dict)
		if environment == 'remote':
			lametric_url = remote_lametric_base_url + lametric_app_id + lametric_app_version
			lametric_headers = {"Accept":"application/json","X-Access-Token": lametric_access_token,"Cache-Control":"no-cache"}
			try:
				lametric_req = requests.post(lametric_url, data=lametric_payload, headers=lametric_headers)
				print(lametric_req2)
			except requests.exceptions.Timeout as e:
				# timeout
				print(e)
			except requests.exceptions.ConnectionError as e:
				# connection error
				print(e)
			except requests.exceptions.RequestException as e:
				# error
				print(e)
		elif environment == 'local':
			lametric_url = local_lametric_base_url + lametric_app_id + lametric_app_version
			lametric_headers = {"Accept":"application/json","X-Access-Token": lametric_access_token,"Cache-Control":"no-cache"}
			try:
				lametric_req = requests.post(lametric_url, data=lametric_payload, headers=lametric_headers, verify=False)
				print(lametric_req)
			except requests.exceptions.Timeout as e:
				# timeout
				print(e)
			except requests.exceptions.ConnectionError as e:
				# connection error
				print(e)
			except requests.exceptions.RequestException as e:
				# error
				print(e)
		else:
			print('no environment!')

	fetch_from_purpleair()
	push_to_lametric()

if __name__ == '__main__':
	try:
		fetch_from_purpleair_and_push_to_lametric()
	except KeyboardInterrupt:
		pass
