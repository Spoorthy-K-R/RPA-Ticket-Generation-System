from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
import os
from typing import Dict, List, Any
import json

# Initialize Gemini API key
# api_key = os.getenv("GOOGLE_API_KEY")
api_key = 'key'

# Categories for email classification
CATEGORIES = ['appreciation', 'suggestion', 'complaint', 'request', 'enquiry']

def categorize_email(email):

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        """Analyze this email and categorize it into one of these categories: {categories}
        Email Subject: {subject}
        Email Body: {body}
        
        Return a JSON in this format:
        {{
            "category": "chosen_category",
            "confidence": confidence_score,
            "reasoning": "brief explanation"
        }}"""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.invoke({
        "categories":CATEGORIES,
        "subject":email['subject'],
        "body":email['body']
    })

    temp=json.loads(result['text'].replace('```json', '').replace('```', '').strip())
    return temp

def validate_form_data(email, ticket):

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    
    # Chain 1: Extract required information
    extraction_prompt = ChatPromptTemplate.from_template(
        """Extract the following information from the email: {required_fields}
        Email Subject: {subject}
        Email Body: {body}
        
        Return a JSON in this format:
        {{
            "extracted_info": {{
                "field_name": "extracted_value",
                ...
            }},
            "missing_fields": ["field1", "field2", ...]
        }}"""
    )
    
    extraction_chain = LLMChain(llm=llm, prompt=extraction_prompt, output_key="extracted_info")
    
    # Chain 2: Validate extracted information
    validation_prompt = ChatPromptTemplate.from_template(
        """Validate if the following information is complete and correct:
        Extracted Information: {extracted_info}
        Required Fields: {required_fields}
        
        Return a JSON in this format:
        {{
            "is_valid": true/false,
            "validation_notes": "notes about validation",
            "missing_fields": ["field1", "field2", ...],
            "incorrect_fields": ["field1", "field2", ...]
        }}"""
    )
    
    validation_chain = LLMChain(llm=llm, prompt=validation_prompt, output_key="validation_result")
    
    # Combine chains
    full_chain = SequentialChain(
        chains=[extraction_chain, validation_chain],
        input_variables=["subject", "body", "required_fields"],
        output_variables=["extracted_info", "validation_result"]

    )
    
    result = full_chain.invoke({
        "subject":email['subject'],
        "body":email['body'],
        "required_fields":ticket['required_details']
    })

    return result 

def generate_response(ticket):

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    memory = ConversationBufferMemory()
    
    prompt = ChatPromptTemplate.from_template(
        """Generate a professional response email for this ticket:
        Category: {category}
        Subject: {subject}
        Status: {status}
        Missing Information: {missing_info}
        
        Previous responses: {chat_history}
        
        Generate a response that:
        1. Acknowledges the customer's email
        2. Requests any missing information politely
        3. Provides next steps
        4. Maintains a professional tone
        5. The mail should have signature as 'RPA Customer Support' at 'Railways Dept'
        6. The generated response should not have any fields that further need to be populated, it should be the exact message that goes out to the customer
        
        Return the response email content directly."""
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt
    )
    
    result = chain.invoke({
        "category":ticket['category'],
        "subject":ticket['subject'],
        "status":ticket['status'],
        "missing_info":ticket.get('missing_info', []),
        "chat_history":ticket.get('response_list', [])
    })

    return result

def extract_and_store_info(email, ticket):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        """Analyze the sentiment of this email:
        Subject: {subject}
        Body: {body}
        
        Return a JSON in this format:
        {{
            "sentiment": "positive/negative/neutral",
            "score": sentiment_score,
            "key_phrases": ["phrase1", "phrase2", ...],
            "urgency_level": "high/medium/low"
        }}"""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(
        subject=email['subject'],
        body=email['body']
    )
    
    return eval(result)  # Convert string JSON to dictionary

def suggest_priority(ticket, sentiment):

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        """Based on the following information, suggest a priority level for this ticket:
        Category: {category}
        Sentiment: {sentiment}
        Urgency Level: {urgency}
        
        Return a JSON in this format:
        {{
            "priority": "high/medium/low",
            "reasoning": "brief explanation"
        }}"""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.invoke({
        "category":ticket['category'],
        "sentiment":sentiment['sentiment'],
        "urgency":sentiment['urgency_level']
    })

    temp=json.loads(result['text'].replace('```json', '').replace('```', '').strip())
    return temp 

