import argparse
import requests
#from requests_toolbelt import MultipartEncoder

def sendtelegrammsg(msg, toid, botid):
 url = f'https://api.telegram.org/bot{botid}/sendMessage?chat_id={toid}&text={msg}'
 sendmsg = requests.get(url)

def main():
  parser = argparse.ArgumentParser()
  parser.add_arguement('--toid', type=str)
  parser.add_arguement('--btid', type=str)
  args = parser.parse_args()
  toid = args.toid
  botid = args.btid
  sendtelegrammsg('hello', toid, btid)

if __name__ == '__main__':
  main()
