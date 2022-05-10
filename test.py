import getpass
import httplib
import json
import re
import ssl
import sys
import time

## admin@10.129.100.82:/var/tmp/ttt /tmp/"
###
PAM_HOSTNAME = "ilcyberweb-pam.teva.corp"
PAM_LOGIN = "/PasswordVault/API/auth/ldap/Logon"
GAIA_ACCOUNT_ID = "236_3"
GAIA_ACC_URL = "/PasswordVault/api/Accounts/263_3/Password/Retrieve"
GAIA_USER = "psadmin"
GAIA_IP = "10.129.100.82"
OLD_FILE_NAME = "/tmp/ILDC.json"
NEW_FILE_NAME = "/tmp/ILDC.json"
GROUP_NAME = "Jump_Servers"
REMOTE_FILE_PASS = GAIA_USER + "@" + GAIA_IP + ":" + OLD_FILE_NAME
LOCAL_FILE_PASS = "/tmp"


def retrieve_gaia_pswd():

    try:
        pam_username = raw_input("Enter username:")
        pam_password = getpass.getpass("Enter password:")

    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(-1)

    try:

        insecure_context = ssl._create_unverified_context()
        conn = httplib.HTTPSConnection(PAM_HOSTNAME, context=insecure_context)

        payload = json.dumps({
            "username": pam_username,
            "password": pam_password
        })

        headers = {
            'Content-Type': 'application/json',
            'Cookie':
            'CA11111= \
             00000002A009FA1FBA8D395FB2E454F21D7A289588A7D91B3D3C82D5EE37FCEC8EC1C61F00000000; \
             CA22222=D81A400903E86AE54D2892CFCC11205242C1A20CFD151D40D85B8803D8D5AAEA; \
             CA33333=; CA55555 = ldap;CAPreferredAuth = ldap;mobileState = \
            Desktop'
        }

        print ("Retrievinf API token ... ")
        conn.request("POST", PAM_LOGIN, payload, headers)
        response = conn.getresponse()
        api_token = json.loads(response.read())
        print(api_token)
        if response.status != 200:
            return ""

        payload = json.dumps({
            "reason": "test",
            "ActionType": "show"
        })

        headers = {
            'Authorization': api_token,
            'Content-Type': 'application/json',
            'Cookie':
                'CA11111=00000002B6A7AC188B2AB0966AF5D60C774AB9F68DBDBBEE7605CF0D11521399120BD43100000000; CA22222=3E325BFEF09950F37E17B5C2F5BEFFEBC3197BC2CF85067D6CA6FC059BD8DE02; CA33333=; CA55555=ldap; CAPreferredAuth=ldap; mobileState=Desktop'
        }
        print ("Retrieving GAIA password from the vault .... ")
        time.sleep(5)
        conn.request("POST", GAIA_ACC_URL, payload, headers)
        response = conn.getresponse()
        dbg_gaia_pass = json.loads(response.read())
        print(dbg_gaia_pass)

        if response.status != 200:
            return ""


    except:
        print("qqq")
        return ""

    return dbg_gaia_pass


########################################################

def scpcopy(DIRECTION, PSWD):
    if DIRECTION == "PULL":
        SCP_CMD = "sshpass -p " + PSWD + " scp " + REMOTE_FILE_PASS + " " + \
                  LOCAL_FILE_PASS
    else:
        SCP_CMD = "sshpass -p " + PSWD + " scp " + LOCAL_FILE_PASS + " " + \
                  REMOTE_FILE_PASS

    try:
        call(SCP_CMD.split(" "))
    except:
        return False

    return True


################      validate IP
###
def ip(ip_address):
    match = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$",
                     ip_address)

    if bool(match) is False:
        print("IP address {} is not valid".format(ip_address))
        return False

    for part in ip_address.split("."):
        if int(part) < 0 or int(part) > 255:
            print("IP address {} is not valid".format(ip_address))
            return False

    print("IP address {} is valid".format(ip_address))

    return True


pswd = retrieve_gaia_pswd()

if pswd == "":
    print("Error retrieving password")
    sys.exit(-1)

if not scpcopy("PULL", pswd):
    print("Error retrieving JSON file")
    sys.exit(-1)

try:
    while True:
        new_ip = raw_input("Enter IP address :")
        if ip(new_ip):
            break
except:
    sys.exit(-1)

####################      Open current JSON file
try:
    with open(OLD_FILE_NAME) as old_file:
        GenericDC = json.load(old_file)
except:
    print("JSON is corrupted or does not exist")
    sys.exit(-1)

for DC_OBJECT, DC_OBJECT_VALUE in GenericDC.items():
    if DC_OBJECT == "objects":

        for x in DC_OBJECT_VALUE:
            if x["name"].upper() == GROUP_NAME.upper():
                print(x["ranges"])
                if new_ip not in x["ranges"]:
                    x["ranges"].append(new_ip)
                print(x["name"] + "::", x["ranges"])
        print(DC_OBJECT_VALUE)
STR_JSON = json.dumps(GenericDC, indent=4, sort_keys=True)
print(STR_JSON)

with open(NEW_FILE_NAME, 'w') as NEW_FILE:
    json.dump(GenericDC, NEW_FILE, indent=4, sort_keys=True)
    NEW_FILE.close()

if scpcopy("PUSH", pswd):
    print("Error sending JSON file")
