from urllib.request import urlopen
import argparse
import time
import boto3


ping_count = 400
ping_delay_secs = 5*60

# Read args
parser = argparse.ArgumentParser(description='Pings an URL during a few days to get information about it\'s execution times')
parser.add_argument('functions', nargs='+', help='Name of the functions to read the info.')
parser.add_argument('--delay', type=int, help='Delay in secs between requests.')

args = parser.parse_args()
functionNames = args.functions

if args.delay is not None: ping_delay_secs = args.delay

print ("Loading API Gateway information...")
# Read API Gateway information
ag = boto3.client("apigateway")
functions = ag.get_rest_apis(limit=500)

# Load all URLs
urls = []

for functionName in functionNames:

	functionGateway = [x for x in functions["items"] if x["name"] == functionName]

	if len(functionGateway) == 0:
		func_list = ", ".join([x["name"] for x in functions["items"]])
		raise Exception(f"Function {functionName} not found. Available functions: {func_list}")

	api_id = functionGateway[0]["id"]
	stages = ag.get_stages(restApiId=api_id)
	stage_name = stages["item"][0]["stageName"]

	#stage = ag.get_stage(restApiId=api_id, stageName=stage_name)
	url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/{stage_name}"

	print(f"Using URL: {url}")
	urls.append(url)


for i in range(1, ping_count):
	for url in urls:
		print(time.strftime("%x %X") + f": Pinging {url}")
		resp = urlopen(url)
		resp.read()

	if ping_delay_secs>0: time.sleep(ping_delay_secs)

print(f"All done! {ping_count} pings done.")
