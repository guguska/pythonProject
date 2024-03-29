import getpass
import httplib
import json
import re
import ssl
import sys
import time
import paramiko

PAM_HOSTNAME = "ilcyberweb-pam.teva.corp"
PAM_LOGIN = "/PasswordVault/API/auth/ldap/Logon"
GAIA_ACCOUNT_ID = "259_3"
GAIA_ACC_URL = "/PasswordVault/api/Accounts/263_3/Password/Retrieve"
GAIA_USER = "psadmin"
GAIA_IP = "10.128.92.44"
GAIA_PORT = 22
REMOTE_PATH = "/tmp/ILDC.json"
LOCAL_PATH = "/tmp/ILDC.json"
GROUP_NAME = "Jump_Servers"
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
            'Content-Type': 'application/json'
        }

        print ("Retrieving API token ... ")
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
            'Content-Type': 'application/json'
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


def scpcopy(direction, gaia_pswd):
    trans = paramiko.Transport((GAIA_IP, GAIA_PORT))
    trans.connect(username=GAIA_USER, password=gaia_pswd)
    sftp = paramiko.SFTPClient.from_transport(trans)

    try:

        if direction != "PULL":
            sftp.put(localpath=LOCAL_PATH, remotepath=REMOTE_PATH)
        else:
            sftp.get(remotepath=REMOTE_PATH, localpath=LOCAL_PATH)

        trans.close()
    except:
        return False

    return True


###########    validate IP
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
except KeyboardInterrupt:
    print("Interrupted")
    sys.exit(-1)

####################      Open current JSON file
try:
    with open(LOCAL_PATH) as old_file:
        GenericDC = json.load(old_file)
except:
    print("JSON is corrupted or does not exist")
    sys.exit(-1)

for dcObject, dcObjectValue in GenericDC.items():
    if dcObject == "objects":

        for x in dcObjectValue:
            if x["name"].upper() == GROUP_NAME.upper():
                print(x["ranges"])
                if new_ip not in x["ranges"]:
                    x["ranges"].append(new_ip)
                print(x["name"] + "::", x["ranges"])
        print(dcObjectValue)
str_json = json.dumps(GenericDC, indent=4, sort_keys=True)
print(str_json)

with open(LOCAL_PATH, 'w') as new_file:
    json.dump(GenericDC, new_file, indent=4, sort_keys=True)
    new_file.close()

if scpcopy("PUSH", pswd):
    print("IP address added successfully")
else:
    print("Error sending JSON file")
