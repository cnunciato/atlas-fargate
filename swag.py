from pulumi_command import local
from pulumi import Output
import requests

def getSwag(swag_url, contact_info):
    # headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    # r = requests.post(swag_url, data=contact_info, headers=headers)

    swag = local.Command("swag",
        create=Output.format("""curl -X POST {1} 
                    -H "Content-Type: application/json"
                    -d {2}""", swag_url, contact_info) 
    )

    # print(create2)
    return swag