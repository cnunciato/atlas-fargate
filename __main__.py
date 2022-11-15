"""An AWS Python Pulumi program"""

import os
import pulumi
from pulumi import Output
import pulumi_docker as docker
import pulumi_aws as aws
import pulumi_awsx as awsx

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
shopping_app_image = awsx.ecr.Image(
    "grocery_list_image",
    repository_url=repo.url,
    path="./fullstack-pulumi-mern-digitalocean")

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


# An ECS cluster to deploy into
cluster = aws.ecs.Cluster("cluster")

# An ALB to serve the container endpoint to the internet
frontend_lb = awsx.lb.ApplicationLoadBalancer("frontend-lb")

# Deploy an ECS Service on Fargate to host the application container
frontend_service = awsx.ecs.FargateService(
    "frontend-service",
    cluster=cluster.arn,
    task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
        container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
            image=shopping_app_image.image_uri,
            cpu=cpu,
            memory=memory,
            essential=True,
            port_mappings=[awsx.ecs.TaskDefinitionPortMappingArgs(
                container_port=container_port,
                target_group=frontend_lb.default_target_group,
            )],
            environment=[{
                "name":"DATABASE_URL",
                "value":"mongodb+srv://admin:admin-password@pulumi-cluster.sgpqtad.mongodb.net/?retryWrites=true"
            },
            {
                "name":"VITE_BACKEND_URL",
                "value":"http://localhost:8000"
            },
            ],
        ),    
    ),
    desired_count=1
)

# An ALB to serve the container endpoint to the internet
backend_lb = awsx.lb.ApplicationLoadBalancer("backend-lb")

# Deploy an ECS Service on Fargate to host the application container
backend_service = awsx.ecs.FargateService(
    "backend-service",
    cluster=cluster.arn,
    task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
        container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
            image=shopping_app_image.image_uri,
            cpu=cpu,
            memory=memory,
            essential=True,
            port_mappings=[awsx.ecs.TaskDefinitionPortMappingArgs(
                container_port=container_port,
                target_group=frontend_lb.default_target_group,
            )],
            environment=[{
                "name":"DATABASE_URL",
                "value":"mongodb+srv://admin:admin-password@pulumi-cluster.sgpqtad.mongodb.net/?retryWrites=true"
            },
            {
                "name":"VITE_BACKEND_URL",
                "value":"http://localhost:8000"
            },
            ],
        ),    
    ),
    desired_count=1
)

# The URL at which the container's HTTP endpoint will be available
pulumi.export("url", Output.concat("http://", frontend_lb.load_balancer.dns_name))
pulumi.export("cluster name", cluster.id)