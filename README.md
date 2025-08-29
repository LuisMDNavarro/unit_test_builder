# Unit Test Builder

## Description
An API developed in Python and deployed on AWS that uses Amazon Bedrock to generate unit tests in Python based on a provided function.

## Technologies
- [Python](https://www.python.org/)
- [AWS](https://aws.amazon.com/)
- [Streamlit](https://streamlit.io/)

### Development
- [pre-commit](https://pre-commit.com/) to keep the code clean
    - [black](https://black.readthedocs.io/en/stable/) to format the code
    - [flake8](https://flake8.pycqa.org/en/latest/) to verify the code
    - [isort](https://pycqa.github.io/isort/) to order imports
    - [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) for various cleaning tasks

### Requirements
- **AWS CLI** installed and configured.
- Install:
    - requests
    - streamlit
    - dotenv

## Steps for deployment and execution

1. From the cmd located in the folder where is the devops.yaml, use the command *aws cloudformation create-stack --stack-name unit-test-builder-devops --template-body file://devops.yaml --capabilities CAPABILITY_NAMED_IAM* to create the Devops Stack.

    - This stack contains the necessary resources before deploying the Unit Test Builder pipeline, just wait for the operation complete.

2. From the cmd located in the folder where is the pipeline.yaml, use the command *aws cloudformation create-stack --stack-name unit-test-builder-pipeline --template-body file://pipeline.yaml --parameters ParameterKey=GitHubConnection,ParameterValue={ARN of your connection}* to create the DePipelinevops Stack.

    - The pipeline will create an deploy the entire project infrastructure, just wait for the operation complete.
    Note: The pipeline retrieves code from a GitHub repository, so you must have your own repository and a connection pointing to it to replicate this project.

3. When the previous step is completed we will have the API URL and Route in the Stack Outputs.

4. The API can be consumed from clients such as Insomia or Postman with the request body structure:

        ``` json
            {
            "session_id": "session_id", //The unique identifier of the session
            "user_request": "user_request", //Your python function
            "language": "English",
            "framework": "unittest",
        }
        ```
5. This project includes a client in streamlit, to use it create your .env file with API_URL = "{the api url}" in the same folder where app.py and from the cmd located in this folder use the command *streamlit run app.py*.
