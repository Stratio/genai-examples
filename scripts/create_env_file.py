"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

import argparse
import json

import os
import ssl
import sys
from http import client
from urllib.parse import urlparse


def get_certificates(certs_path):
    print(f"Checking certificates in {certs_path}")
    if not os.path.exists(certs_path):
        print(f"=> Folder {certs_path} does not exist")
        sys.exit(1)
    files = os.listdir(certs_path)
    username = None
    for file in files:
        if file.endswith("_private.key"):
            username = file.split("_private")[0]
            break
    if username is None:
        print(
            f"=> Private key not found in {certs_path}. It should be named as <username>_private.key"
        )
        sys.exit(1)
    else:
        print(f"=> Detected certificates for user {username}")
    client_cert = os.path.join(certs_path, f"{username}.crt")
    if not os.path.exists(client_cert):
        print(f"=> Client certificate {client_cert} not found")
        sys.exit(1)
    client_key = os.path.join(certs_path, f"{username}_private.key")
    if not os.path.exists(client_key):
        print(f"=> Client key {client_key} not found")
        sys.exit(1)
    ca_cert = os.path.join(certs_path, "ca-cert.crt")
    if not os.path.exists(ca_cert):
        print(f"=> CA certificate {ca_cert} not found")
        sys.exit(1)
    print(f"=> Certificates OK!")
    return client_cert, client_key, ca_cert


def get_proxy_url(proxy_url, certs):
    print(f"Checking proxy URL {proxy_url}")
    client_cert, client_key, ca_cert = certs
    # parse the url
    parsed_url = urlparse(proxy_url)
    scheme = parsed_url.scheme
    if scheme != "https":
        print(f"=> Proxy URL should be HTTPS")
        sys.exit(1)
    host = parsed_url.hostname
    port = parsed_url.port or 8080
    # test the connection
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(certfile=client_cert, keyfile=client_key)
    context.load_verify_locations(cafile=ca_cert)
    context.verify_mode = ssl.CERT_REQUIRED
    conn = client.HTTPSConnection(host, port, context=context)
    conn.request("GET", "/")
    response = conn.getresponse()
    data = response.read().decode()
    if response.status != 200:
        print(
            f"=> Proxy URL response status is not 200. HTTP status: {response.status} Response: {data}"
        )
        sys.exit(1)
    if not "Welcome to GenAI Developer Proxy!" in data:
        print(f"=> Proxy URL response is not as expected. Response: {data}")
    conn.close()
    data_json = json.loads(data)
    # get enabled services
    enabled_services = []
    for key, value in data_json["services"].items():
        if value["enabled"]:
            enabled_services.append(key)
    print(f"=> Enabled services: {', '.join(enabled_services)}")
    # eg: https://genai-api.s000001-genai:8080
    genai_api_host = urlparse(
        data_json["services"]["genai-api"]["internal_url"]
    ).hostname
    print(f"=> GenAI API service name: {genai_api_host}")
    url = f"{scheme}://{host}:{port}"
    print(f"=> Proxy URL OK!")
    return url, genai_api_host


def create_env_file(proxy_url, certs, genai_api_host, format):
    print(f"Creating genai.env file")
    proxy_host = urlparse(proxy_url).hostname
    proxy_port = urlparse(proxy_url).port
    client_cert, client_key, ca_cert = certs
    genai_api_tenant = genai_api_host.split(".")[1].split("-")[0]
    (maybe_export, maybe_quote, ext) = ("export ", '"' ,"sh") if format == 'bash' else ("", "", "env")
    env_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"genai-env.{ext}"))
    with open(env_file_path, "w") as f:
        f.write(f"{maybe_export}GENAI_API_SERVICE_NAME={maybe_quote}{genai_api_host}{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_API_TENANT={maybe_quote}{genai_api_tenant}{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_API_REST_URL={maybe_quote}{proxy_url}{maybe_quote}/service/genai-api\n")
        f.write(f"{maybe_export}GENAI_API_REST_USE_SSL=true\n")
        f.write(f"{maybe_export}GENAI_API_REST_CLIENT_CERT={maybe_quote}{client_cert}{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_API_REST_CLIENT_KEY={maybe_quote}{client_key}{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_API_REST_CA_CERTS={maybe_quote}{ca_cert}{maybe_quote}\n")
        f.write(f"\n")
        f.write(f"{maybe_export}GENAI_GATEWAY_URL={maybe_quote}{proxy_url}/service/genai-gateway{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_GATEWAY_USE_SSL=true\n")
        f.write(f"{maybe_export}GENAI_GATEWAY_CLIENT_CERT={maybe_quote}{client_cert}{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_GATEWAY_CLIENT_KEY={maybe_quote}{client_key}{maybe_quote}\n")
        f.write(f"{maybe_export}GENAI_GATEWAY_CA_CERTS={maybe_quote}{ca_cert}{maybe_quote}\n")
        f.write(f"\n")
        f.write(f"{maybe_export}VAULT_LOCAL_CLIENT_CERT={maybe_quote}{client_cert}{maybe_quote}\n")
        f.write(f"{maybe_export}VAULT_LOCAL_CLIENT_KEY={maybe_quote}{client_key}{maybe_quote}\n")
        f.write(f"{maybe_export}VAULT_LOCAL_CA_CERTS={maybe_quote}{ca_cert}{maybe_quote}\n")
        f.write(f"\n")
        f.write(f"{maybe_export}VIRTUALIZER_BASE_PATH=/service/virtualizer={maybe_quote}/service/virtualizer{maybe_quote}\n")
    print(f"=> Created genai.env file in {env_file_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certs_path", type=str, help="Folder with user certificates.", required=True
    )
    parser.add_argument(
        "--proxy_url",
        type=str,
        help="Stratio GenAI Developer Proxy URL.",
        required=True,
    )
    parser.add_argument(
        "--format",
        type=str,
        help="Output format. 'env' for .env files to add to PyCharm, or 'bash' for .sh files to source in your terminal.",
        required=True
    )
    args = parser.parse_args()

    certs = get_certificates(args.certs_path)
    proxy_url, genai_api_host = get_proxy_url(args.proxy_url, certs)
    create_env_file(proxy_url, certs, genai_api_host, args.format)


if __name__ == "__main__":
    main()
