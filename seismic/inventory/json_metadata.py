"""
Use Json file to store station extra metadata

Fei Zhang
2020-07-11

# TODO: Design a proper json metadata structure to encaptulate all the metadata items. store in the extra tag of stationxml file
"""
import json

def read_orientation_correction(in_json_file):
  """ Read in a json file
  :param in_json_file:
  :return:
  """
  # load a file

  with open(in_json_file) as f:
    data = json.load(f)

  print(type(data))

  print(data.keys()) # dict_keys(['7X.MA01', '7X.MA11', '7X.MA12', '7X.MA13', '7X.MA14', '7X.MA21', '7X.MA22'.....)]

  netsta = "OA.CF28" # '7X.MA01'

  print(data[netsta])

  print(data[netsta]['date_range'], type(data[netsta]['date_range'])) # ['2009-09-10T02:57:07.160000Z', '2010-06-05T05:35:00.623400Z'] <class 'list'>
  print(data[netsta]['azimuth_correction'], type(data[netsta]['azimuth_correction'])) # 38.0 <class 'float'>

if __name__ == "__main__":
  # json_file = "/Datasets/Orientation_Correction_json/7X_ori_error_estimates.json"
  json_file = "OA_ori_error_estimates.json" #"7X_ori_error_estimates.json"
  read_orientation_correction(json_file)