
import requests
import xml.etree.ElementTree as ET

ISE_Server= "192.168.1.1"

url = f"https://{ISE_Server}:443/ers/config/profilerprofile/?filter=name.eq.AIRTAME-Device"

payload = ""
headers = {
  'Accept': 'application/xml',
  'Authorization': 'BASICAUTHCREDHERE'   #Make sure you edit this
}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)
xml=ET.fromstring(response.content)
ProfileID = xml[0][0].attrib['id']

url = f"https://{ISE_Server}:443/api/v1/endpoint?filter=profileId.eq."+ProfileID
headers = {
  'Authorization': 'BASICAUTHCREDHERE'   #Make sure you edit this
}
response = requests.request("GET", url, headers=headers, data=payload, verify=False)

data = response.json()
listofmacs = []
for item in data:
  listofmacs.append(item['mac'])

for item in listofmacs:
  url = f"https://{ISE_Server}/admin/API/mnt/Session/MACAddress/"+item
  response = requests.request("GET", url, headers=headers, data=payload, verify=False)
  searchableString=str(response.content)
  MAC=item
  Switch=(searchableString[searchableString.find("<device_ip_address>"):searchableString.find("</device_ip_address>")])
  Switch=Switch[Switch.find(">")+1:]
  PSN=(searchableString[searchableString.find("<destination_ip_address>"):searchableString.find("</destination_ip_address>")])
  PSN=PSN[PSN.find(">")+1:]
  MntNode=(searchableString[searchableString.find("<acs_server>"):searchableString.find("</acs_server>")])
  MntNode=MntNode[MntNode.find(">")+1:]
  
  url = f"https://{ISE_Server}:443/admin/API/mnt/CoA/Disconnect/{MntNode}/{MAC}/1/{Switch}/{PSN}"
  response = requests.request("GET", url, headers=headers, data=payload, verify=False)
