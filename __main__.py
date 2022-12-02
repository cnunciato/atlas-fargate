"""An AWS + MongoDB Cloud Python Pulumi program"""

import re
import pulumi
from pulumi import Output
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_mongodbatlas as mongodb

# Get configuration
config = pulumi.Config()
