"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

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


def build_env_var(name, value, file_format):
    (maybe_export, maybe_quote) = (
        ("export ", '"') if file_format == "bash" else ("", "")
    )
    return f"{maybe_export}{name}={maybe_quote}{value}{maybe_quote}\n"


def create_env_file(proxy_url, certs, genai_api_host, file_format):
    file_ext = "sh" if file_format == "bash" else "env"
    file_name = f"genai-env.{file_ext}"
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
    print(f"Creating {file_name} file")
    client_cert, client_key, ca_cert = certs
    genai_api_tenant = genai_api_host.split(".")[1].split("-")[0]
    proxy_host = urlparse(proxy_url).hostname
    proxy_port = urlparse(proxy_url).port
    with open(file_path, "w") as f:
        f.write("# AVAILABLE in GenAI-API!\n")
        f.write(build_env_var("GENAI_API_SERVICE_NAME", genai_api_host, file_format))
        f.write(build_env_var("GENAI_API_TENANT", genai_api_tenant, file_format))
        f.write(
            build_env_var(
                "GENAI_API_REST_URL", f"{proxy_url}/service/genai-api", file_format
            )
        )
        f.write(build_env_var("GENAI_API_REST_USE_SSL", "true", file_format))
        f.write(build_env_var("GENAI_API_REST_CLIENT_CERT", client_cert, file_format))
        f.write(build_env_var("GENAI_API_REST_CLIENT_KEY", client_key, file_format))
        f.write(build_env_var("GENAI_API_REST_CA_CERTS", ca_cert, file_format))
        f.write(
            build_env_var(
                "GENAI_GATEWAY_URL", f"{proxy_url}/service/genai-gateway", file_format
            )
        )
        f.write(build_env_var("GENAI_GATEWAY_USE_SSL", "true", file_format))
        f.write(build_env_var("GENAI_GATEWAY_CLIENT_CERT", client_cert, file_format))
        f.write(build_env_var("GENAI_GATEWAY_CLIENT_KEY", client_key, file_format))
        f.write(build_env_var("GENAI_GATEWAY_CA_CERTS", ca_cert, file_format))
        f.write("\n")
        f.write("# NOT AVAILABLE in GenAI-API!\n")
        f.write(build_env_var("VAULT_LOCAL_CLIENT_CERT", client_cert, file_format))
        f.write(build_env_var("VAULT_LOCAL_CLIENT_KEY", client_key, file_format))
        f.write(build_env_var("VAULT_LOCAL_CA_CERTS", ca_cert, file_format))
        f.write(build_env_var("VIRTUALIZER_HOST", proxy_host, file_format))
        f.write(build_env_var("VIRTUALIZER_PORT", str(proxy_port), file_format))
        f.write(
            build_env_var("VIRTUALIZER_BASE_PATH", "/service/virtualizer", file_format)
        )
        f.write(
            build_env_var(
                "OPENSEARCH_URL", f"{proxy_url}/service/opensearch", file_format
            )
        )
        f.write(
            build_env_var(
                "GOVERNANCE_URL", f"{proxy_url}/service/governance", file_format
            )
        )
    print(f"=> Created {file_name} file in {file_path}")


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
    args = parser.parse_args()

    certs = get_certificates(args.certs_path)
    proxy_url, genai_api_host = get_proxy_url(args.proxy_url, certs)
    create_env_file(proxy_url, certs, genai_api_host, "env")
    create_env_file(proxy_url, certs, genai_api_host, "bash")


if __name__ == "__main__":
    main()
