# flake8: noqa
import json

import boto3
import botocore

REGION = "us-east-1"
AGENT_ARN = "arn:aws:bedrock:us-east-1:355631997030:agent/CSSEIG51ET"


def lambda_handler(event, context):
    connection_id = event["requestContext"].get("connectionId")
    domain_name = event["requestContext"].get("domainName")
    stage = event["requestContext"].get("stage")

    if not connection_id or not domain_name or not stage:
        return {"statusCode": 400}

    gateway = boto3.client(
        "apigatewaymanagementapi", endpoint_url=f"https://{domain_name}/{stage}"
    )

    message = {"message": "Hola desde Lambda!"}

    try:
        client = boto3.client("bedrock-agentcore", region_name=REGION)
        body = json.loads(event["body"])
        user_request = body.get("user_request")
        session_id = body.get("session_id")
        if not session_id:
            message = {"message": "Missing 'session_id"}
            gateway.post_to_connection(
                ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
            )

        if not user_request:
            message = {"message": "Missing 'user_request"}
            gateway.post_to_connection(
                ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
            )

        if len(user_request) > 10000:
            message = {"message": "Request too large"}
            gateway.post_to_connection(
                ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
            )

        payload_bytes = json.dumps(
            {
                "inputText": user_request,
                "language": body.get("language", "English"),
                "framework": body.get("framework", "pytest"),
            }
        ).encode("utf-8")

        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_ARN,
            mcpSessionId=session_id,
            payload=payload_bytes,
            contentType="application/json",
            accept="application/json",
        )

        gateway.post_to_connection(
            ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
        )
    except gateway.exceptions.GoneException:
        message = {"error": f"Connection {connection_id} is gone"}
        gateway.post_to_connection(
            ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
        )
    except client.exceptions.ResourceNotFoundException:
        message = {"error": "Agent not found"}
        gateway.post_to_connection(
            ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
        )
    except (
        client.exceptions.ThrottlingException,
        botocore.eventstream.EventStreamError,
    ):
        message = {"error": "Too many requests"}
        gateway.post_to_connection(
            ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
        )
    except Exception as e:
        message = {"error": str(e)}
        gateway.post_to_connection(
            ConnectionId=connection_id, Data=json.dumps(message).encode("utf-8")
        )
    finally:
        return {"statusCode": 200}
