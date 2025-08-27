import json
import os

import boto3
import botocore

REGION = os.environ.get("REGION")
AGENT_ARN = os.environ.get("AGENT_ARN")
AGENT_ID = os.environ.get("AGENT_ID")
ALIAS_ID = os.environ.get("ALIAS_ID")


def lambda_handler(event, context):
    try:
        client = boto3.client("bedrock-agent-runtime", region_name=REGION)
        body = json.loads(event["body"])
        user_request = body.get("user_request")
        session_id = body.get("session_id")

        if not session_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'session_id'"}),
            }

        if not user_request:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'user_request'"}),
            }

        if len(user_request) > 10000:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Request too large"}),
            }

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

        gateway = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{event['requestContext']['domainName']}"
            f"/{event['requestContext']['stage']}",
        )

        connection_id = event["requestContext"]["connectionId"]

        for event_chunk in response:
            data_bytes = event_chunk["chunk"]["bytes"]
            gateway.post_to_connection(ConnectionId=connection_id, Data=data_bytes)

    except client.exceptions.ResourceNotFoundException:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Agent not found"}),
        }
    except (
        client.exceptions.ThrottlingException,
        botocore.eventstream.EventStreamError,
    ):
        return {
            "statusCode": 429,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Too many requests"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
