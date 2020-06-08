import os
import json
import docker

from docker import errors


class DockerHandler:
    def __init__(self, config_path, logger):
        self.logger = logger
        self.logger.info('Starting docker handler.')

        with open(config_path) as config_file:
            self.config = json.load(config_file)
        for service in self.config['services']:
            service['full_name'] = f'{self.config["registry"]}/{service["name"]}:latest'
            service['full_path'] = os.path.join(self.config['root_path'], service['path'])

        self.logger.info(f'Obtaining client from {self.config["socket"]}.')
        self.client = docker.DockerClient(
            base_url=self.config['socket'],
        )
        self.logger.info('DockerHandler ready.')

    def list_services_from_config(self):
        return [service['name'] for service in self.config['services']]

    def list_services_from_client(self):
        return [service.name for service in self.client.services.list()]

    def get_service_from_repo(self, repo, branch):
        for service in self.config['services']:
            if service['github_repo'] == repo and service['github_branch'] == branch:
                return service

    def build_image(self, service):
        try:
            self.logger.info(f'{service["name"]}: Building image on {service["full_path"]}.')
            self.client.images.build(
                path=service['full_path'],
                tag=service['full_name'],
                dockerfile='arm.Dockerfile'
            )
        except TypeError:
            self.logger.error(f'Error on provided path {service["full_path"]}, check configuration file.')
        except errors.BuildError:
            self.logger.error(f'Failed to build {service["name"]}.')
        except errors.APIError:
            self.logger.error(f'Server error while building {service["name"]}.')

    def push_image(self, service):
        try:
            self.logger.info(f'Pushing image {service["full_name"]}.')
            self.client.images.push(repository=service['full_name'])
        except errors.APIError:
            self.logger.error(f'Server error while pushing {service["name"]}.')

    def remove_service(self, service):
        for running_service in self.client.services.list():
            if running_service.name == service['name']:
                self.logger.info(f'Service with name {service["name"]} detected, removing.')
                try:
                    running_service.remove()
                except errors.APIError:
                    self.logger.error(f'Server error while removing {service["name"]}.')

    def create_service(self, service):
        try:
            self.logger.info(f'Creating service {service["name"]}')
            self.client.services.create(
                image=service['full_name'],
                name=service['name'],
                constraints=self.config['constraints'],
            )
        except errors.APIError:
            self.logger.error(f'Server error while creating {service["name"]}.')

    def service_full_deploy(self, service):
        self.build_image(service)
        self.push_image(service)
        self.remove_service(service)
        self.create_service(service)

    def config_run(self):
        for service in self.config['services']:
            self.service_full_deploy(service)
