# AWS-SSM-Backup
AWS Systems Manager document for EC2 AMI backup


### Instructions

These are the deployment steps until the full implementation is complete.

#### Parameter description

PROJECTNAME: The name of the system.
ROLENAME: Classification of instances.
ENVIRONMENT: The name of the environment.

#### Set variables

Locally(terminal), run following commands.

```bash
$ PROJECTNAME=ac
$ ROLENAME=ifsv
$ ENVIRONMENT=dev
```

#### Create a VPC environment

```bash
$ aws cloudformation create-stack \
    --stack-name $PROJECTNAME-$ROLENAME-$ENVIRONMENT-vpc \
    --region ap-northeast-1 \
    --template-body file://vpc_privatelink.yml \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameters \
    ParameterKey=ProjectName,ParameterValue=$PROJECTNAME \
    ParameterKey=RoleName,ParameterValue=$ROLENAME \
    ParameterKey=Environment,ParameterValue=$ENVIRONMENT
```


#### Create Lambda Functions for SSM
```
$ aws cloudformation create-stack \
    --stack-name $PROJECTNAME-$ENVIRONMENT-Lambda-for-SSM-Automation \
    --region ap-northeast-1 \
    --template-body file://ami-lambda.yml \
    --capabilities CAPABILITY_NAMED_IAM
```


#### Create SSM Automation

```
$ aws cloudformation create-stack \
    --stack-name $PROJECTNAME-$ENVIRONMENT-SSM-Automation \
    --region ap-northeast-1 \
    --template-body file://SSM-Backup.yml \
    --capabilities CAPABILITY_NAMED_IAM
```