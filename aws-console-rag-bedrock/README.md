# AWS Console Integration of RAG
## Step 1: Create S3 Bucket
* On **Amazon S3 Console**, create an S3 bucket that will contain the necessary files for FAQ or internal sources. 
* All setting will remain default
* Block Public Access is enabled
* Versioning is Enabled
* Once S3 Bucket is created, Upload FAQ/SOP Document

## Step 2: Create Knoweledge Base in Bedrock
* Navigate to **Amazon Bedrock Console**
* On the naviagation pannel, select **Knowledge Bases** and click Create
* Enter a **Name** for the Knowledge Base with vector store
* Add a **Description** for better contect
* Under IAM permissions section, **Create and use a new service role**
* **Connect Data Source**, which in this case is S3
* Under **S3 URI**, click Browse S3 to link the knowledge base to the S3 Bucket containing the internal document (FAQ/SOP Document)
* Every other settings remain default

## Step 3: Configure Embeddings
* On the next page of Knowledge Base creation, we are going to configure the Embeddings settings 
* **Select Model**, chose the model provider and in this it is **Amazon** using its **Titan Text Embedding G1 - Text**
* For **Inference Settings** we will keep the majority default depending on project requirements
* For **Vectore Store Stype**, we will select **Anazon S3 Vectors** to store the created vector embeddings that the Knowledge Base will provide to the LLM model for RAG implementation. 
* Review the Settings and Create the Knowledge Base
* **Sync the Knowledge Base** to re-index the content

>**Note:** If there are issus in syncing the Knowledge Base and it mentions **Data Sync Failed, Too Many >Requests**. This could be from the **Service Quota limit** of the chosen Model and the Invoke Request >limit. Depending on the Account this may require to communicate with Amazon Support to increase the limit.

## Step 4: Creating BackEnd (Lambda Function)


