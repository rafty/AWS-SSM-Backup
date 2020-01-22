# -*- coding: utf-8 -*-
import boto3
from botocore.exceptions import ClientError
from retrying import retry
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def retry_if_client_error(exception):
    # falseを返すまでリトライする
    logger.warning('_is_retryable_exception: {}, '.format(exception))
    return not isinstance(exception, ClientError)


def _is_retryable_exception(exception):
    # falseを返すまでリトライする
    logger.warning('_is_retryable_exception: {}, '.format(exception))
    return not isinstance(exception, ClientError) or \
        exception.response["Error"]["Code"] in ["InvalidSnapshot.InUse"]


class EC2(object):
    def __init__(self, region=None):
        self._client = boto3.client('ec2')

    @retry(wait_exponential_multiplier=500,
           stop_max_delay=62000,
           retry_on_exception=retry_if_client_error)
    def describe_instances(self):

        response = self._client.describe_instances()

        instance_images = list()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_images.append((instance['InstanceId'], instance['ImageId']))

        # describe_instancesのpaging
        while 'NextToken' in response:
            response = self._client.describe_instances(NextToken=response['NextToken'])
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_images.append((instance['InstanceId'], instance['ImageId']))

        return instance_images

    @retry(wait_exponential_multiplier=500,
           stop_max_delay=62000,
           retry_on_exception=retry_if_client_error)
    def describe_images(self):
        logger.info('describe_images:')
        response = self._client.describe_images(Owners=["self"])

        instance_images = list()
        for image in response['Images']:
            instance_images.append(image)

        # paging for describe_images
        while 'NextToken' in response:
            response = self._client.describe_images(NextToken=response['NextToken'])
            for image in response['Images']:
                instance_images.append(image)
        return instance_images

    def list_instance_image(self, instance_id):
        instance_image_list = self.describe_images()
        listed_images = self.extract_instance(instance_image_list, instance_id)
        sorted_images = self.sort_list(listed_images)
        logger.info('instance_list: {}'.format(sorted_images))
        return sorted_images

    @staticmethod
    def extract_instance(instance_image_list, instance_id):
        listed_images = [{ 'Name': img['Name'],
                           'ImageId': img['ImageId'],
                           'BlockDeviceMappings': img['BlockDeviceMappings']
                         }
                         for img in instance_image_list
                         if img['Name'].startswith('backup_' + instance_id)]
        return listed_images

    @staticmethod
    def sort_list(listed_images):
        sorted_images = sorted(listed_images, key=lambda x: x['Name'])
        return sorted_images

    def delete_ami_and_snapshot(self, delete_list):
        logger.info('delete_ami_and_snapshot: {}, '.format(delete_list))

        if len(delete_list) <= 0:
            logger.info('no deregister_ami_and_snapshot:')
            return

        for ami in delete_list:
            self._client.deregister_image(ImageId=ami.get('ImageId'))
            logger.info('deregister image: {}, '.format(ami))

        for ami in delete_list:
            self.delete_snapshots(ami)
            logger.info('delete snapshots: {}'.format(ami))

    # retry_on_exception: falseを返すまでリトライする。
    # wait_exponential_multiplier: 2 ^ n x 1000ミリ秒
    # wait_exponential_max: 最大待機時間は 10秒
    @retry(retry_on_exception=_is_retryable_exception,
           wait_exponential_multiplier=1000,
           wait_exponential_max=10000)
    def delete_snapshots(self, ami):
        logger.info('delete snapshot: {}, '.format(ami))
        for dev in ami.get('BlockDeviceMappings'):
            if not 'Ebs' in dev:
                continue
            snapshot_id = dev['Ebs']['SnapshotId']
            self._client.delete_snapshot(SnapshotId=snapshot_id)
