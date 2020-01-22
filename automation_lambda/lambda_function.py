# -*- coding: utf-8 -*-
import logging
from aws_ec2 import EC2

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def extract_delete_snapshot_over_generation(instance_image_list, generation):
    delete_list = list()
    if len(instance_image_list) > generation:
        delete_list = instance_image_list[0:-generation]
        logger.info('delete_list: {}, '.format(delete_list))
    return delete_list


def lambda_handler(event, context):
    logger.info('lambda_handler event: {}, '
                'context: {}'.format(event, context))

    instance_id = event.get('InstanceId', None)
    generation = int(event.get('Generation', '3'))

    if not instance_id:
        logger.error('instance is none')
        return True

    ec2 = EC2()
    instance_image_list = ec2.list_instance_image(instance_id)
    logger.info('instance_image_list: {}, '.format(instance_image_list))

    deletion = extract_delete_snapshot_over_generation(
        instance_image_list, generation)
    ec2.delete_ami_and_snapshot(deletion)
    logger.info('instance_image_list: {}, '.format(deletion))
    return True
