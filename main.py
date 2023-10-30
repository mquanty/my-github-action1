import requests
#from requests_toolbelt import MultipartEncoder

def sendtelegrammsg(msg, toid, botid):
 url = f'https://api.telegram.org/bot{botid}/sendMessage?chat_id={toid}&text={msg}'
 sendmsg = requests.get(url)

def main():
  toid = os.environ['TG_ID']
  botid = os.environ['TG_BOT']
  sendtelegrammsg('hello', toid, btid)

if __name__ == '__main__':
  main()
