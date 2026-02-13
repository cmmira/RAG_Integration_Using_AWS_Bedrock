import json
import os
import boto3

# Environment variables:
# BEDROCK_REGION     -> e.g. "us-east-1"
# KNOWLEDGE_BASE_ID  -> Bedrock Knowledge Base ID
# MODEL_ARN          -> ARN of the model you have access to
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]

bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

def lambda_handler(event, context):
    """Handle HTTP requests from the browser via Lambda Function URL."""
    try:
        # Detect HTTP method (works for Function URL & API Gateway-style events)
        method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
            or event.get("httpMethod")
        )

        # 1) CORS preflight
        if method == "OPTIONS":
            return _response(200, {"message": "CORS preflight OK"})

        # 2) Only allow POST for normal requests
        if method != "POST":
            return _response(405, {"error": f"Method {method} not allowed"})

        # Parse JSON body from the browser
        body = json.loads(event.get("body") or "{}")

        question = (body.get("question") or "").strip()
        user_context = (body.get("context") or "").strip()

        if not question:
            return _response(400, {"error": "Field 'question' is required."})

        # Optional extra hint for retrieval
        full_input = question
        if user_context:
            full_input = f"{question}\\n\\nAdditional context from user:\\n{user_context}"

        # Call Bedrock Knowledge Base with explicit modelArn
        resp = bedrock_agent.retrieve_and_generate(
            input={"text": full_input},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        # ----- Extract answer text safely -----
        answer_text = ""
        output = resp.get("output", {})

        text_field = output.get("text")

        if isinstance(text_field, str):
            # Most common shape: text is a simple string
            answer_text = text_field.strip()
        elif isinstance(text_field, list):
            # Fallback if AWS ever returns a list of blocks
            for block in text_field:
                if isinstance(block, dict) and "text" in block:
                    answer_text += str(block["text"])
            answer_text = answer_text.strip()

        if not answer_text:
            answer_text = "No answer returned from Knowledge Base."

        # Optional: count retrieved references for display
        citation_count = 0
        for c in resp.get("citations", []):
            citation_count += len(c.get("retrievedReferences", []))

        result = {
            "answer": answer_text,
            "citation_count": citation_count,
        }

        return _response(200, result)

    except Exception as e:
        print("Error:", e)
        return _response(500, {"error": f"Internal error: {str(e)}"})

def _response(status_code, body):
    """Build HTTP response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
        },
        "body": json.dumps(body),
    }