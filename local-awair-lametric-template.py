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

# replace "123.456.78.9" with your Awair device IP address
awair_url = 'http://123.456.78.9/air-data/latest'
# get your LaMetric Time api_key here -> https://developer.lametric.com/user/devices
lametric_access_token = 'your_api_key_here'
# lametric_basic_auth = 'placeholder'

remote_lametric_base_url = 'https://developer.lametric.com/api/v1/dev/widget/update/'
# replace "9.87.654.321" with your LaMetric Time device IP address
local_lametric_base_url = 'https://9.87.654.321:4343/api/v1/devices/widget/update/'
# update this if you clone the LaMetric Time app
lametric_app_id = 'com.lametric.941c51dff3135bd87aa72db9d855dd50/'
# latest version at the time of publishing
lametric_app_version = '2'

first_frame = json.loads('{"text":"AWAIR","icon":"37314","index":0}')
lametric_frames_list = []
lametric_frames_list.append(first_frame)
lametric_frames_dict = {}

def get_from_awair_and_push_to_lametric():
	def fetch_from_awair():
		try:
			awair_req = requests.get(awair_url)
			sensors_dict = json.loads(awair_req.text)
			print(json.dumps(sensors_dict))
			build_lametric_frames(sensors_dict)
		except requests.exceptions.Timeout as e:
			# timeout
			print e
		except requests.exceptions.ConnectionError as e:
			# connection error
			print e
		except requests.exceptions.RequestException as e:
			# error
			print e

	def build_lametric_frames(sensors):
		for sensor in sensors.keys():
			if sensor == 'score':
				score = sensors['score']
				frame_item = {"text": str(score),"icon":"37314","index":1}
				lametric_frames_list.append(frame_item)
			elif sensor == 'temp':
				deg = u'\xb0'
				temp = sensors['temp']
				if(temp_unit == 'f'):
					temp = (temp * (9/5)) + 32
				frame_item = {"text": str(round(temp, 2)) + deg + "C","icon":"a2422","index":2}
				lametric_frames_list.append(frame_item)
			elif sensor == 'humid':
				humid = sensors['humid']
				frame_item = {"text": str(humid) + "% RH","icon":"a2423","index":3}
				lametric_frames_list.append(frame_item)
			elif sensor == 'co2':
				co2 = sensors['co2']
				frame_item = {"text": str(co2) + " ppm","icon":"a2440","index":4}
				lametric_frames_list.append(frame_item)
			elif sensor == 'voc':
				voc = sensors['voc']
				frame_item = {"text": str(voc) + " ppb","icon":"a37364","index":5}
				lametric_frames_list.append(frame_item)
			elif sensor == 'pm25':
				pm25 = sensors['pm25']
				frame_item = {"text": str(pm25) + " ug/m3","icon":"a8522","index":6}
				lametric_frames_list.append(frame_item)
			elif sensor == 'lux':
				lux = sensors['lux']
				frame_item = {"text": str(lux) + " lux","icon":"a1338","index":7}
				lametric_frames_list.append(frame_item)
			elif sensor == 'spl_a':
				spl_a = sensors['spl_a']
				frame_item = {"text": str(spl_a) + " dba","icon":"a5888","index":8}
				lametric_frames_list.append(frame_item)
			else:
				erroneous = sensor
				# print(erroneous)

	def push_to_lametric():
		lametric_frames_dict['frames'] = sorted(lametric_frames_list, key = lambda i: i['index'])
		print(json.dumps(lametric_frames_dict))
		lametric_payload = json.dumps(lametric_frames_dict)
		
		if(environment == 'remote'):
			lametric_url = remote_lametric_base_url + lametric_app_id + lametric_app_version
			lametric_headers = {"Accept":"application/json","X-Access-Token": lametric_access_token,"Cache-Control":"no-cache"}
			try:
				lametric_req = requests.post(lametric_url, data=lametric_payload, headers=lametric_headers)
				print(lametric_req.text)
			except requests.exceptions.Timeout as e:
				# timeout
				print e
			except requests.exceptions.ConnectionError as e:
				# connection error
				print e
			except requests.exceptions.RequestException as e:
				# error
				print e
		elif(environment == 'local'):
			lametric_url = local_lametric_base_url + lametric_app_id + lametric_app_version
			lametric_headers = {"Accept":"application/json","X-Access-Token": lametric_access_token,"Cache-Control":"no-cache"}
			try:
				lametric_req = requests.post(lametric_url, data=lametric_payload, headers=lametric_headers, verify=False)
				print(lametric_req.text)
			except requests.exceptions.Timeout as e:
				# timeout
				print e
			except requests.exceptions.ConnectionError as e:
				# connection error
				print e
			except requests.exceptions.RequestException as e:
				# error
				print e
		else:
			print('no environment!')

	fetch_from_awair()
	push_to_lametric()

if __name__ == '__main__':
	try:
		get_from_awair_and_push_to_lametric()
	except KeyboardInterrupt:
		pass