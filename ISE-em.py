### Import needed modules
import keyring
import requests
import base64
import xml.etree.ElementTree as ET

### Enter Required Info
ISE_Server = "X.X.X.X"
WLC_IP = "X.X.X.X"

### Import Credentials from windows credential manager
credentials = keyring.get_credential("AirTame_ISE_Reboot_script", None)
credentials = f"{credentials.username}:{credentials.password}"
B64Creds = base64.b64encode(credentials.encode()).decode()

### Define getHeaders Functions
def getHeaders(AppType):
  headers = {}
  if AppType == "":
    headers = {
      'Authorization': f'Basic {B64Creds}',
    }
  else:
    headers = {
      'Accept': AppType,
      'Authorization': f'Basic {B64Creds}',
    }
  return headers

### MAIN ###

# URL creation and get and parse to grab airtame Profiler Profile ID
url = f"https://{ISE_Server}:443/ers/config/profilerprofile/?filter=name.eq.AIRTAME-Device"
response = requests.request("GET", url, headers = getHeaders("application/xml"), verify=False)
xml=ET.fromstring(response.content)
ProfileID = xml[0][0].attrib['id']

# URL to set up for paging through filtered endpoints
url = f"https://{ISE_Server}:443/api/v1/endpoint?filter=profileId.eq."+ProfileID

# while pagnation (going page by page until nothing) is true, add every endpoint mac to a list. then, add one to the page count and search the next page. 
pagnationOngoing = True
listofmacs = []
page = 1
while pagnationOngoing:
  response = requests.request("GET", url+"&size=100&page="+str(page), headers = getHeaders(""), verify=False)
  try:
    data = response.json()
    for item in data:
      listofmacs.append(item['mac'])
# if searchign through pages fails, it means there is no more data because the page doesnt exist. Close the loop
    page+=1
  except:
    pagnationOngoing = False

# now using that list of macs, start creating a url list of all the airtames with ongoing sessions that can be bounced. In addition, filter out all wireless connections because were doing a port bounce on ethernet ports
bounceList = []
for item in listofmacs:
  url = f"https://{ISE_Server}/admin/API/mnt/Session/MACAddress/"+item
  response = requests.request("GET", url, headers = getHeaders(""), verify=False)
# if the response is an ok, parse through that data to get everythign you need for a coa port bounce api call. DO NOT include any with the network device as our WLC IP, bcause we're only looking to do the ones wired in
  if response.status_code == 200:
    searchableString=str(response.content)
    NetworkDevice=(searchableString[searchableString.find("<device_ip_address>"):searchableString.find("</device_ip_address>")])
    NetworkDevice=NetworkDevice[NetworkDevice.find(">")+1:]
    if WLC_IP not in NetworkDevice:
      MAC=item
      PSN=(searchableString[searchableString.find("<destination_ip_address>"):searchableString.find("</destination_ip_address>")])
      PSN=PSN[PSN.find(">")+1:]
      MntNode=(searchableString[searchableString.find("<acs_server>"):searchableString.find("</acs_server>")])
      MntNode=MntNode[MntNode.find(">")+1:]
# build your urls for the call
      bounceurl = f"https://{ISE_Server}:443/admin/API/mnt/CoA/Disconnect/{MntNode}/{MAC}/1/{NetworkDevice}/{PSN}"
      bounceList.append(bounceurl)

#make the calls
for bounceurl in bounceList:
  print(bounceurl)
  #requests.request("GET", bounceurl, headers = getHeaders(""),  verify=False)

