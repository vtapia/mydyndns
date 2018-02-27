from flask import Flask, request, json
import threading
import os
import logging
import yaml
import string
import random

logwrkzg = logging.getLogger('werkzeug')
logwrkzg.setLevel(logging.ERROR)
chwrkzg = logging.StreamHandler()
logwrkzg.addHandler(chwrkzg)

logger = logging.getLogger('mydyndns')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %T')
ch.setFormatter(fmt)
logger.addHandler(ch)

cfg_path = os.getcwd() + '/config/'
cfg_file = cfg_path + 'mydyndns.conf'

with open(cfg_file, 'r') as f:
        cfg = yaml.load(f)

server = Flask(__name__)


class RegisteredDomains:
    def __init__(self):
        self.lock = threading.Lock()
        self.domains = {}

    def update_domain(self, req_data, ip):
        if req_data['domain'] in self.domains:
            self.domains[req_data['domain']]['ip'] = ip
            return True
        return False

    def verify_domain_password(self, req_data):
        if self.domains[req_data['domain']]['password'] == req_data['password']:
            return True
        return False

    def create_empty_domain(self, req_data, ip):
        self.domains[req_data['domain']] = {}
        self.domains[req_data['domain']]['ip'] = ip
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
        self.domains[req_data['domain']]['password'] = password
        return password


@server.route("/api/domain/update", methods=["POST"])
def domain_update():
    req_data = request.get_json(force=True)
    ip = request.remote_addr
    if 'domain' in req_data:
        if registered_domain_name(req_data):
            logger.info("Domain \"%s\" update requested" % req_data['domain'])
            config = server.config['domainlist']
            if 'password' in req_data:
                if config.verify_domain_password(req_data):
                    config.update_domain(req_data, ip)
                    logger.info("Domain \"%s\" updated with ip \"%s\"" % (req_data['domain'], ip))
                    return ('Domain updated', 201)
                else:
                    logger.error("Wrong domain password for \"%s\"", req_data['domain'])
                    return(412)
            else:
                logger.error("No domain password for \"%s\"", req_data['domain'])
                return(412)
        else:
            logger.error("Update requested for non-existent \"%s\"" % req_data['domain'])
            return(412)
    else:
        return("Missing domain name in request", 412)


@server.route("/api/domain/list", methods=["POST"])
def domain_get():
    req_data = request.get_json(force=True)
    logger.debug(req_data)
    with open(cfg_file, 'r') as f:
        cfg = yaml.load(f)

    if req_data['password'] == cfg['admin_password']:
        info = server.config['domainlist'].domains
        logger.debug(info)
        return (json.dumps(info), 200)
    else:
        logger.error('Missing admin password')
        return(412)


@server.route("/api/domain/create", methods=["post"])
def domain_create():
    '''
    Request must include domain + admin password (set in config file)
    Will return key for the subdomain
    '''
    req_data = request.get_json(force=True)
    logger.debug(req_data)
    if 'domain' in req_data:
        if registered_domain_name(req_data):
            logger.error("Domain \"%s\" already exists" % req_data['domain'])
            return (412)
        else:
            with open(cfg_file, 'r') as f:
                cfg = yaml.load(f)

            if req_data['password'] == cfg['admin_password']:
                ip = request.remote_addr
                config = server.config['domainlist']
                password = config.create_empty_domain(req_data, ip)
                return (password, 200)
            else:
                logger.error("Wrong admin password")
                return (412)
    else:
        return('Missing domain name', 412)


@server.route("/api/server/kill", methods=["DELETE"])
def server_kill():
    kill_server()
    return ('', 204)


@server.route("/api/server/status", methods=["GET"])
def server_status():
    return ('Server running', 200)


def start_server(cfg):
    with open(cfg_file, 'r') as f:
        cfg = yaml.load(f)

    if cfg['debug']:
        logwrkzg.setLevel(logging.INFO)
        logger.setLevel(logging.DEBUG)

    server.config['domainlist'] = RegisteredDomains()

    logger.info("Listening to port %s" % cfg['port'])
    server.run("0.0.0.0", cfg['port'])


def kill_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def registered_domain_name(req_data):
    if 'domain' in req_data:
        domains = server.config['domainlist'].domains
        if req_data['domain'] in domains:
            return True
        else:
            logger.info("%s is not a registered domain" % req_data['domain'])
            return False
    else:
        logger.error("The request does not include a domain name")
        return False


if __name__ == "__main__":
    start_server(cfg)
