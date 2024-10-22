### Import needed
import requests
import xml.etree.ElementTree as ET

### Define ISE-IP
ISE_Server= "X.X.X.X"   #### make sure you edit this

### Get URL of profile-id for airtames
url = f"https://{ISE_Server}:443/ers/config/profilerprofile/?filter=name.eq.AIRTAME-Device"
### set up payload and headers to get authorized
payload = ""
headers = {
  'Accept': 'application/xml',
  'Authorization': 'Basic XXXXXXXXX',   #Make sure you edit this
}
### Send call and parse data to get the ID
response = requests.request("GET", url, headers=headers, data=payload, verify=False)
xml=ET.fromstring(response.content)
ProfileID = xml[0][0].attrib['id']

### Make a baseurl and headers that will search through multiple pages of endpoints that have that profile
baseurl = f"https://{ISE_Server}:443/api/v1/endpoint?filter=profileId.eq."+ProfileID
headers = {
  'Authorization': 'Basic XXXXXXXXXX',   #Make sure you edit this
}
### while pagnation (going page by page until nothing) is true, add every endpoint mac to a list. then, add one to the page count and search the next page. 
pagnationOngoing = True
listofmacs = []
page = 1
while pagnationOngoing:
  response = requests.request("GET", baseurl+"&size=100&page="+str(page), headers=headers, data=payload, verify=False)
  try:
    data = response.json()
    for item in data:
      listofmacs.append(item['mac'])
### if searchign through pages fails, it means there is no more data because the page doesnt exist. Close the loop
    page+=1
  except:
    pagnationOngoing = False

### for every mac in the list you just made, get session info for each
for item in listofmacs:
  url = f"https://{ISE_Server}/admin/API/mnt/Session/MACAddress/"+item
  response = requests.request("GET", url, headers=headers, data=payload, verify=False)
### if the response is an ok, parse through that data to get everythign you need for a coa port bounce api call
  if response.status_code == 200:
    searchableString=str(response.content)
    MAC=item
    Switch=(searchableString[searchableString.find("<device_ip_address>"):searchableString.find("</device_ip_address>")])
    Switch=Switch[Switch.find(">")+1:]
    PSN=(searchableString[searchableString.find("<destination_ip_address>"):searchableString.find("</destination_ip_address>")])
    PSN=PSN[PSN.find(">")+1:]
    MntNode=(searchableString[searchableString.find("<acs_server>"):searchableString.find("</acs_server>")])
    MntNode=MntNode[MntNode.find(">")+1:]
### build you url for the call
    url = f"https://{ISE_Server}:443/admin/API/mnt/CoA/Disconnect/{MntNode}/{MAC}/1/{Switch}/{PSN}"
### make the call
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
  
