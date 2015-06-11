#!/usr/bin/env python
# pylint: disable=no-value-for-parameter
import click


@click.command()
@click.argument('template_path')
@click.argument('output_path')
@click.argument('docker_ip')
def create(template_path, output_path, docker_ip):
    with open(template_path, 'r') as template_file:
        template = template_file.read()
    output = template.replace('DOCKER_IP', docker_ip)
    with open(output_path, 'w') as output_file:
        output_file.write(output)

if __name__ == '__main__':
    create()
