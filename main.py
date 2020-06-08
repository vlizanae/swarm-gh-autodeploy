import json
import logging
from abc import ABC

from tornado import web, ioloop
from docker_handler import DockerHandler

logging.basicConfig(level=logging.INFO)


class HTTPHandler(web.RequestHandler, ABC):
    SUPPORTED_METHODS = ('POST',)
    logger = logging.getLogger()
    docker_handler = DockerHandler('/root/setup.json', logger)

    def post(self):
        data = json.loads(self.request.body)
        repo = data['repository']['full_name']
        branch = data['ref'].split('/')[-1]
        self.logger.info(f'Request received for repo {repo} on branch {branch}.')

        service = self.docker_handler.get_service_from_repo(repo, branch)
        if service:
            self.logger.info('Service found in config file.')
            self.set_status(202)
        else:
            self.logger.info('Service not found in config file.')
            self.set_status(204)
        self.flush()

        if service:
            self.logger.info('Starting service deploy.')
            self.docker_handler.service_full_deploy(service)


if __name__ == '__main__':
    server = web.Application([('/', HTTPHandler)])
    server.listen(80)
    ioloop.IOLoop.current().start()
