"""An AWS Python Pulumi program"""

import os
import pulumi
from pulumi import Output
import pulumi_docker as docker
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_mongodbatlas as mongodb
import re


# get configuration
config = pulumi.Config()
frontend_port = config.require_int("frontendPort")
backend_port = config.require_int("backendPort")
mongo_port = config.require_int("mongoPort")
mongo_host = config.require("mongoHost") # Note that strings are the default, so it's not `config.require_str`, just `config.require`.
database = config.require("database")
node_environment = config.require("nodeEnvironment")
protocol = config.require("protocol")

# AWS configs
container_port = config.get_int("containerPort", 80)
cpu = config.get_int("cpu", 1024)
memory = config.get_int("memory", 1024)

# MongoDB Atlas configs
db_username = config.get_object("dbUser", "test-acc-username")
db_password = config.get_secret_object("dbPassword", "test-acc-password")
atlas_org_id = config.get_object("orgID", "635a171e8eed17676af01b5a")

stack = pulumi.get_stack()

# network = docker.Network("network", name=f"services-{stack}")

# # Local MongoDB Community container image
# mongo_image = docker.RemoteImage("mongo_image",
#     name='mongo',
#     keep_locally=True
# )

# mongo_local_container = docker.Container("mongo_local_container",
#     image=mongo_image.latest,
#     ports=[{
#         "internal": 27017,
#         "external": 27017
#     }],
#     networks_advanced=[docker.ContainerNetworksAdvancedArgs(
#         name=network.name
#     )],
# )

# An ECR repository to store our application's container image
repo = awsx.ecr.Repository("grocery_list_repo")

# Build and publish our application's container image from ./fullstack-pulumi-mern-digitalocean to the ECR repository
# shopping_app_image = awsx.ecr.Image(
#     "grocery_list_image",
#     repository_url=repo.url,
#     path="./fullstack-pulumi-mern-digitalocean")

frontend_image = awsx.ecr.Image(
    "grocery_frontend_image",
    repository_url=repo.url,
    path="./app/frontend")

backend_image = awsx.ecr.Image(
    "grocery_backend_image",
    repository_url=repo.url,
    path="./app/backend")
# shopping_app_container = docker.Container("shopping_app_container",
#     image=shopping_app_image.image_uri,
#     ports=[{
#         "internal": 5173,
#         "external": 5173
#     }],
#     networks_advanced=[docker.ContainerNetworksAdvancedArgs(
#         name=network.name
#     )],
#     envs=[
#         "DATABASE_URL=mongodb+srv://admin:admin-password@pulumi-cluster.sgpqtad.mongodb.net/?retryWrites=true",
#     ],
# )


# Create MongoDB Project
mongo_project = mongodb.Project("mongo_project", org_id="635a171e8eed17676af01b5a")

# Open access to all IPs
mongo_acl = mongodb.ProjectIpAccessList("mongo_acl",
    cidr_block="0.0.0.0/0",
    comment="Open access for backend",
    project_id=mongo_project.id,)

# Create Free Tier Project
mongo_cluster = mongodb.Cluster("mongo-cluster",
    backing_provider_name="AWS",
    project_id=mongo_project.id,
    provider_instance_size_name="M0",
    provider_name="TENANT",
    provider_region_name="US_WEST_2")

# Create Database user and give access to the cluster and database
mongo_user = mongodb.DatabaseUser("db_user",
    auth_database_name="admin",
    labels=[mongodb.DatabaseUserLabelArgs(
        key="project",
        value="pulumi",
    )],
    password=db_password,
    project_id=mongo_project.id,
    roles=[
        mongodb.DatabaseUserRoleArgs(
            database_name="grocery-list",
            role_name="readWrite",
        ),
        mongodb.DatabaseUserRoleArgs(
            database_name="admin",
            role_name="readAnyDatabase",
        ),
    ],
    scopes=[
        mongodb.DatabaseUserScopeArgs(
            # Extracts the cluster name to add to database scopes
            name=Output.all(mongo_cluster.srv_address).apply(lambda v: re.split("\.|\/\/", v[0])[1]),
            type="CLUSTER",
        ),
    ],
    username=db_username)


# An ECS cluster to deploy into
cluster = aws.ecs.Cluster("cluster")

# An ALB to serve the frontend service to the internet
frontend_lb = awsx.lb.ApplicationLoadBalancer("frontend-lb")

# Deploy an ECS Service on Fargate to host the application container
frontend_service = awsx.ecs.FargateService(
    "frontend-service",
    cluster=cluster.arn,
    task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
        containers={
            "front": awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                image=frontend_image.image_uri,
                cpu=cpu,
                memory=memory,
                essential=True,
                port_mappings=[awsx.ecs.TaskDefinitionPortMappingArgs(
                    container_port=container_port,
                    target_group=frontend_lb.default_target_group,
                )],
                environment=[{
                    "name":"VITE_BACKEND_URL",
                    "value":"http://localhost:8000" 
                },
                ],
            ),
            "back": awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                image=backend_image.image_uri,
                cpu=cpu,
                memory=memory,
                essential=True,
                port_mappings=[awsx.ecs.TaskDefinitionPortMappingArgs(
                    container_port=8000,
                    host_port=8000
                )],
                environment=[{
                    "name":"DATABASE_URL",
                    "value":Output.format("mongodb+srv://{0}:{1}@{2}", db_username, db_password, 
                                Output.all(mongo_cluster.srv_address).apply(lambda v: v[0].split("//"))[1])
                },
                ],
            ),
        }    
    ),
    desired_count=1
)



# MongoDB Atlas exports
pulumi.export("mongo cluster id", mongo_cluster.cluster_id)
pulumi.export("mongo uri", mongo_cluster.mongo_uri)
pulumi.export("mongo srv address", mongo_cluster.srv_address)
pulumi.export("mongo connection string", 
    Output.format("mongodb+srv://{0}:{1}@{2}", db_username, db_password, 
    Output.all(mongo_cluster.srv_address).apply(lambda v: v[0].split("//"))[1])
)
# pulumi.export("name", mongo_cluster.get("mongo_cluster", mongo_cluster.id).name)
# The URL at which the container's HTTP endpoint will be available
# pulumi.export("backend url", Output.concat("http://", backend_lb.load_balancer.dns_name))
pulumi.export("frontend url", Output.concat("http://", frontend_lb.load_balancer.dns_name))
pulumi.export("cluster name", cluster.id)
