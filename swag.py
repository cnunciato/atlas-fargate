from pulumi_command import local
from pulumi import Output


def getSwag(swag_url, contact_info):

    create2=Output.format("""curl -X POST {1} 
                    -H "Content-Type: application/json"
                    -d {2}""", swag_url, contact_info) 
    swag = local.Command("swag",
        create=Output.format("""curl -X POST {1} 
                    -H "Content-Type: application/json"
                    -d {2}""", swag_url, contact_info) 
    )

    print(create2)
    return swag