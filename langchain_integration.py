from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
import os
from typing import Dict, List, Any

# Initialize Gemini API key
api_key = os.environ.get["GOOGLE_API_KEY"]

# Categories for email classification
CATEGORIES = ['appreciation', 'suggestion', 'complaint', 'request', 'enquiry']

def categorize_email(email):
    """
    Categorize email using LangChain and Gemini.
    
    Args:
        email (Dict[str, str]): Dictionary containing 'subject' and 'body' of the email
        
    Returns:
        Dict[str, Any]: Dictionary containing category and confidence score
    """
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
    result = chain.run(
        categories=CATEGORIES,
        subject=email['subject'],
        body=email['body']
    )
    
    return result 

def validate_form_data(email, ticket):
    """
    Validate and extract required information from email using LangChain.
    
    Args:
        email (Dict[str, str]): Dictionary containing email data
        ticket (Dict[str, Any]): Dictionary containing ticket information
        
    Returns:
        Dict[str, Any]: Dictionary containing validation results and extracted information
    """
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
    
    extraction_chain = LLMChain(llm=llm, prompt=extraction_prompt)
    
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
    
    validation_chain = LLMChain(llm=llm, prompt=validation_prompt)
    
    # Combine chains
    full_chain = SequentialChain(
        chains=[extraction_chain, validation_chain],
        input_variables=["subject", "body", "required_fields"]
    )
    
    result = full_chain.run(
        subject=email['subject'],
        body=email['body'],
        required_fields=ticket['required_details']
    )
    
    return result  

def generate_response(ticket):
    """
    Generate a response email using LangChain.
    
    Args:
        ticket (Dict[str, Any]): Dictionary containing ticket information
        
    Returns:
        str: Generated response email content
    """
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
        
        Return the response email content directly."""
    )
    
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )
    
    return chain.run(
        category=ticket['category'],
        subject=ticket['subject'],
        status=ticket['status'],
        missing_info=ticket.get('missing_info', []),
        chat_history=ticket.get('response_list', [])
    )

def extract_and_store_info(email, ticket):
    """
    Analyze the sentiment of the email using LangChain.
    
    Args:
        email (Dict[str, str]): Dictionary containing email data
        
    Returns:
        Dict[str, Any]: Dictionary containing sentiment analysis results
    """
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

def suggest_priority(ticket: Dict[str, Any], sentiment: Dict[str, Any]) -> str:
    """
    Suggest ticket priority based on category and sentiment.
    
    Args:
        ticket (Dict[str, Any]): Dictionary containing ticket information
        sentiment (Dict[str, Any]): Dictionary containing sentiment analysis results
        
    Returns:
        str: Suggested priority level
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        """Based on the following information, suggest a priority level for this ticket:
        Category: {category}
        Subject: {subject}
        Sentiment: {sentiment}
        Urgency Level: {urgency}
        
        Return a JSON in this format:
        {{
            "priority": "high/medium/low",
            "reasoning": "brief explanation"
        }}"""
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(
        category=ticket['category'],
        subject=ticket['subject'],
        sentiment=sentiment['sentiment'],
        urgency=sentiment['urgency_level']
    )
    
    return eval(result)  # Convert string JSON to dictionary 