
import getopt
import json
import re
import sys
import uuid

# admin@10.129.100.82:/var/tmp/ttt /tmp/"
###
PAM_HOSTNAME = "ilcyberweb-pam.teva.corp"
PAM_LOGIN = "/PasswordVault/API/auth/ldap/Logon"
GAIA_ACCOUNT_ID = "236_3"
GAIA_ACC_URL = "/PasswordVault/api/Accounts/263_3/Password/Retrieve"
GAIA_USER = "psadmin"
GAIA_IP = "10.129.100.82"
OLD_FILE_NAME = "/tmp/ILDC.json"
NEW_FILE_NAME = "ILDC.json"
GROUP_NAME = "Jump_Servers"
REMOTE_FILE_PASS = GAIA_USER + "@" + GAIA_IP + ":" + OLD_FILE_NAME
LOCAL_FILE_PASS = "/tmp"


print sys.argv

def getparam(argv):
	#   argv = sys.argv[1:]
	ADD_GROUP_ARG = False
	GROUP_NAME_ARG= "Jump_Servers"
	NEW_IP_ARG = ""
	try:
		opts, args = getopt.getopt(argv, "ha:g:i:", ["addgroup=", "gname=", "ipaddr="])
	except getopt.GetoptError:
		print 'Usage help'
		sys.exit(1)
	for opt, arg in opts:
		if opt == '-h':
			print 'Usage help'
			sys.exit()
		elif opt in ("-a", "--addgroup"):
			GROUP_NAME_ARG = arg
			ADD_GROUP_ARG = True
		elif opt in ("-g", "--gname"):
			GROUP_NAME = arg
		elif opt in ("-i", "--ipaddr"):
			NEW_IP_ARG = arg

	return ADD_GROUP_ARG, GROUP_NAME_ARG,NEW_IP_ARG


def ip(ip_address):
	match = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip_address)

	if bool(match) is False:
		print("IP address {} is not valid".format(ip_address))
		return False

	for part in ip_address.split("."):
		if int(part) < 0 or int(part) > 255:
			print("IP address {} is not valid".format(ip_address))
			return False

	print("IP address {} is valid".format(ip_address))

	return True


ADD_GROUP, GROUP_NAME,NEW_IP = getparam(sys.argv[1:])

print 'Group name is ', GROUP_NAME
print 'IP address  is ', NEW_IP
print 'Add group is ', ADD_GROUP
try:
	with open(OLD_FILE_NAME) as old_file:
		GenericDC = json.load(old_file)
except:
	print("JSON is corrupted or does not exist")
	sys.exit(-1)

if ADD_GROUP:
	EXISTING_GROUPS = GenericDC.get("objects")
	print json.dumps(EXISTING_GROUPS, indent=4)
	for x in EXISTING_GROUPS:

		if x["name"].upper() == GROUP_NAME.upper():
			print("Duplicate group name")
			break

	NEW_GROUP = {}
	GROUP_ID = str(uuid.uuid4())
	GROUP_DESC = ""
	GROUP_RANGE = []

	NEW_GROUP["name"] = GROUP_NAME
	NEW_GROUP["ranges"] = GROUP_RANGE
	NEW_GROUP["description"] = ""
	NEW_GROUP["id"] = GROUP_ID

	EXISTING_GROUPS.append(NEW_GROUP)
	print json.dumps(EXISTING_GROUPS, indent=4)
