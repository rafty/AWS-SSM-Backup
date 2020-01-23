# AWS-SSM-Backup
AWS Systems Manager document for EC2 AMI backup


## Instructions

These are the deployment steps until the full implementation is complete.

### Parameter description

PROJECTNAME: The name of the system.  
ROLENAME: Classification of instances.  
ENVIRONMENT: The name of the environment.  
YOURNAME: The Bucket name prefix.  

### Set variables

Locally(terminal), run following commands.

```bash
$ PROJECTNAME=ac
$ ROLENAME=ifsv
$ ENVIRONMENT=dev
$ YOURNAME=yagita
```

### Create a VPC environment

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

### Create Lambda Functions for SSM

__Install python package.__
```bash
$ cd lambda/layer/python
$ pip install -r requirements.txt -t .
$ cd ../../..
```

__Create a bucket to upload lambda functions.__
```bash
$ aws s3 mb s3://$YOURNAME-$PROJECTNAME
```

```bash
$ aws cloudformation package \
    --template-file ami-lambda.yml \
    --s3-bucket $YOURNAME-$PROJECTNAME \
    --output-template-file packaged.yml

$ aws cloudformation deploy \
    --stack-name $PROJECTNAME-$ENVIRONMENT-Lambda-for-SSM-Automation \
    --region ap-northeast-1 \
    --template-file packaged.yml \
    --capabilities CAPABILITY_NAMED_IAM \
    --output text
```


### Create SSM Automation

```
$ aws cloudformation create-stack \
    --stack-name $PROJECTNAME-$ENVIRONMENT-SSM-Automation \
    --region ap-northeast-1 \
    --template-body file://SSM-Backup.yml \
    --capabilities CAPABILITY_NAMED_IAM
```
