import requests, json, os, traceback

chromeuseragent =  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36' #"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/507.12 (KHTML, like Gecko) Chrome/25.31.00.00 Safari/507.12" #"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100001" #'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
naukri_accesstoken, naukri_logouttoken = '', ''
UPDATE_PROFILE = True

NAUKRI_login_url     = 'https://www.naukri.com/central-login-services/v1/login'
NAUKRI_dashboard_url = 'https://www.naukri.com/servicegateway-mynaukri/resman-aggregator-services/v0/users/self/dashboard'
NAUKRI_profile_url   = 'https://www.naukri.com/servicegateway-mynaukri/resman-aggregator-services/v2/users/self?expand_level=2'
NAUKRI_update_url    = 'https://www.naukri.com/servicegateway-mynaukri/resman-aggregator-services/v0/users/self/fullprofiles'
#NAUKRI_inbox_url     = 'https://www.naukri.com/servicegateway-mynaukri/resman-aggregator-services/v0/inbox/users/self/mails'
to_update = {}

def sendTelegramMsg(msg, toid=None, botid=None):
    if msg is None or msg == '': return
    if not botid: botid = os.environ['TG_BT']
    if not toid: toid = os.environ['TG_ID']
    url = f'https://api.telegram.org/bot{botid}/sendMessage?chat_id={toid}&text={msg}'
    sendmsg = requests.get(url)
    # print(sendmsg.json())

def getdict2getstr(getdict):
    getstrlist = []
    for k, v in getdict.items():
        kstr = k
        if k.startswith('!'):
            kstr = k.replace('!', '')
        if type(v) is list:
            getstrlist.extend([kstr + '=' + str(x) for x in v])
        else:
            if v is None or v == '':
                continue #skip for none or empty string
            getstrlist.append(kstr + '=' + str(v))
    getstr = '?' + '&'.join(getstrlist)
    getstr = getstr.replace(' ', '%20').replace(',', '%2C')
    return getstr

def naukri():
    telegramMessage = ''
    try:
        username = os.environ['NK_ID']
        password = os.environ['NK_PW']

        s = requests.Session()

        # LOGIN
        #print('\nLOGIN')
        body1 = {'username': username, 'password': password}
        sendTelegramMsg(str(body1))
        x1 = s.post(NAUKRI_login_url, json=body1, headers={
            'content-type': 'application/json',
            "accept": "application/json",
            'User-Agent': chromeuseragent,
            'appid': '103',
            'systemid': 'jobseeker',
            'clientid': 'd3skt0p'
        })
        sendTelegramMsg(x1.text)
        result1 = json.loads(x1.text)
        cookies = result1['cookies']
        searchcookie, nauk_rt, nauk_sid, nauk_otl = '', '', '', ''
        for i in cookies:
            if i['name'] == 'nauk_at': naukri_accesstoken = 'Bearer ' + i['value']
            if i['name'] == 'nauk_rt': naukri_logouttoken, nauk_rt = 'ACCESSTOKEN=' + i['value'], 'nauk_rt=' + i['value'] + ';'
            if i['name'] == 'nauk_sid': nauk_sid = 'nauk_sid=' + i['value'] + ';'
            if i['name'] == 'nauk_otl': nauk_otl = 'nauk_otl=' + i['value'] + ';'
        searchcookie = nauk_rt
        searchcookie2 = nauk_rt + nauk_sid + nauk_otl
        #cookiestring = '; '.join([c['name']+'='+c['value'] for c in cookies])

        #sendTelegramMsg(naukri_accesstoken)

        userinfo = result1['userInfo']
        telegramMessage += f"Naukri Login from {userinfo['ipAddress']}\n"

        raise Exception("skipped\n")
        
        # DASHBOARD
        x8 = s.get(NAUKRI_dashboard_url, headers={
            'content-type': 'application/json',
            "accept": "application/json",
            'User-Agent': chromeuseragent,
            'authorization': naukri_accesstoken,
            'appid': '105',
            'systemid': 'Naukri',
            'clientid': 'd3skt0p',
        })
        result8 = json.loads(x8.text)
        if 'dashBoard' in result8:
            dashboard = result8['dashBoard']
            dashboardprint = {
                # 'username': result8['dashBoard']['username'],
                'name': dashboard['name'],
                'Total Experience': dashboard['rawTotalExperience'],
                'Current CTC': dashboard['rawCtc'],
                'Recruiter Actions': f"{dashboard['profileViewCount']}, {dashboard['recruiterActionsLatestDate']}",
                'Search Appearances': f"{dashboard['totalSearchAppearancesCount']}, {dashboard['totalSearchAppearancesLatestDate']}",
                'Profile Id': dashboard['profileId'],
                'Last Modified': dashboard['mod_dt'],
            }
            #print(json.dumps(dashboardprint, indent='\t'))
            telegramMessage += f"Name: {dashboard['name']}\n"
            telegramMessage += f"{dashboard['profileViewCount']} Recruiter Actions since {dashboard['recruiterActionsLatestDate']}\n"
            telegramMessage += f"{dashboard['totalSearchAppearancesCount']} Search Appearances since {dashboard['totalSearchAppearancesLatestDate']}\n"
            telegramMessage += f"Profile Last Modified at {dashboard['mod_dt']}\n"

        # READ PROFILE
        x2 = s.get(NAUKRI_profile_url, headers={
            'content-type': 'application/json',
            "accept": "application/json",
            'User-Agent': chromeuseragent,
            'authorization': naukri_accesstoken,
            'appid': '105',
            'systemid': 'Naukri',
        })
        result2 = json.loads(x2.text)
        #for eachp in result2['profile']:
        to_update['keySkills'] = result2['profile'][0]['keySkills']
        to_update['resumeHeadline'] = result2['profile'][0]['resumeHeadline']
        to_update['summary']: result2['profile'][0]['summary']
        profile1id = result2['profile'][0]['profileId']  # or result8['dashBoard']['profileId']

        if UPDATE_PROFILE:
            body3 = { "profile": to_update, "profileId": profile1id }
            x3 = s.post(NAUKRI_update_url, json=body3, headers={
                "accept": "application/json",
                'content-type': 'application/json',
                'authorization': naukri_accesstoken,
                'User-Agent': chromeuseragent,
                'appid': '105',
                'systemid': 'Naukri',
                'clientid': 'd3skt0p',
                "x-http-method-override": "PUT",
            })
            result3 = json.loads(x3.text)
            if 'profile' in result3:
                for eachpf in result3['profile']:
                    if eachpf['id'] == profile1id:
                        #print('profile updated successfully')
                        telegramMessage += 'profile updated successfully\n'

        # LOGOUT
        x4 = s.post(NAUKRI_login_url, data='{}', headers={
            'accept': "application/json, text/javascript, */*; q=0.01",
            'content-type': 'application/json',
            'authorization': naukri_logouttoken,
            'appid': '105',
            'systemid': 'jobseeker',
            'clientid': 'd3skt0p',
            "x-http-method-override": "DELETE",
        })
        result4 = json.loads(x4.text)
        if result4['userInfo'] is None or result4['userStateInfo'] is None:
            #print('logout successful')
            telegramMessage += 'Naurki Logout Successful'
    except Exception as e:
        errorstring = f"Exception: [{type(e).__name__}] at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
        sendTelegramMsg(errorstring)
    finally:
        sendTelegramMsg(telegramMessage)

if __name__ == '__main__':
    #naukri()
    sendTelegramMsg('hello')
