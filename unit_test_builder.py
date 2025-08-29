import json
import os

import boto3
import botocore

# Variables received from the template
REGION = os.environ.get("REGION")
AGENT_ID = os.environ.get("AGENT_ID")
ALIAS_ID = os.environ.get("ALIAS_ID")


# Main function
def lambda_handler(event, context):
    try:
        # Client to invoke the agent
        client = boto3.client("bedrock-agent-runtime", region_name=REGION)
        # Retrieve the request body
        body = json.loads(event["body"])
        # User request (code)
        user_request = body.get("user_request")
        # User session ID
        session_id = body.get("session_id")

        # Validation of the existence of session_id
        if not session_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'session_id'"}),
            }

        # Validation of the existence of user_request
        if not user_request:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'user_request'"}),
            }

        # Code length, if it is longer the agent may take a long time and cause a timeout
        if len(user_request) > 300:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"error": "Request too large, maximum allowed: 300 characters."}
                ),
            }

        # Invoking the agent by passing the promptSessionAttributes (user preferences)
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

        # Response initialization
        response_text = ""

        # Iterates over the events received in the Bedrock agent response
        for response_event in response["completion"]:
            # Checks if the event contains a data fragment (chunk)
            if "chunk" in response_event:
                # Gets the bytes of the chunk
                data = response_event["chunk"]["bytes"]
                # Decodes bytes to UTF-8 text and concatenates it into response_text
                response_text += data.decode("utf8")

        # Returns the response obtained from the agent
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
        # Returns an error if the agent does not exist
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Agent not found"}),
        }
    except (
        client.exceptions.ThrottlingException,
        botocore.eventstream.EventStreamError,
    ):
        # Returns an error if too many requests are made too quickly.
        return {
            "statusCode": 429,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Too many requests"}),
        }
    except Exception as e:
        # Return an error for any other problem
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
