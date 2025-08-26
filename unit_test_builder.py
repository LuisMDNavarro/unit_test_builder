import json
import os

import boto3
import botocore

REGION = os.environ.get("REGION")
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

        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id,
            inputText=user_request,
            sessionState={
                "promptSessionAttributes": {
                    "language": body.get("language", "English"),
                    "framework": body.get("framework", "pytest"),
                }
            },
        )

        response_text = ""

        for response_event in response["completion"]:
            if "chunk" in response_event:
                data = response_event["chunk"]["bytes"]
                response_text += data.decode("utf8")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "api_response": response_text,
                }
            ),
        }
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
