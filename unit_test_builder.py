import json
import os

import boto3

REGION = os.environ.get("REGION")
AGENT_ID = os.environ.get("AGENT_ID")
ALIAS_ID = os.environ.get("ALIAS_ID")


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        code = body.get("code")
        session_id = body.get("session_id")
        client = boto3.client("bedrock-agent-runtime", region_name=REGION)

        if not code:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing 'code'"})}

        if not session_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'session_id'"}),
            }

        if len(code) > 10000:
            return {"statusCode": 400, "body": json.dumps({"error": "Code too large"})}

        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id,
            inputText=code,
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
                    "code": response_text,
                }
            ),
        }
    except client.exceptions.ResourceNotFoundException:
        return {"statusCode": 404, "body": json.dumps({"error": "Agent not found"})}
    except client.exceptions.ThrottlingException:
        return {"statusCode": 429, "body": json.dumps({"error": "Too many requests"})}
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
