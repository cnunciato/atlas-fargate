# MongoDB Atlas + AWS Fargate Example
This is an example of a MERN stack deployed on AWS Fargate and MongoDB Atlas. 

![arch diagram](/architecture.png)

## Instructions
- Export [AWS credentials](https://www.pulumi.com/registry/packages/aws/installation-configuration/)
- Export [MongoDB Cloud credentials](https://www.pulumi.com/registry/packages/mongodbatlas/installation-configuration/)
- Initialize Pulumi stack `pulumi stack init dev`
- Set AWS region `pulumi config set aws:region us-west-2`
- Set MongoDB Cloud org value in Pulumi config `pulumi config set orgID [value]`
- Set DB username in Pulumi config `pulumi config set dbUser [value]`
- Set DB password in Pulumi config `pulumi config set dbPassword [value] --secret`
- `pulumi up`