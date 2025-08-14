#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI API connection and configuration.
This will help ensure the API key and configuration are working correctly.
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
API_KEY = os.getenv("OPENAI_API_KEY", "xxxxxxxxxxx")
API_VERSION = "2025-01-01-preview"
AZURE_ENDPOINT = "https://your-openai-resource.openai.azure.com"
DEPLOYMENT_NAME = "xxxxx"

def test_azure_openai_connection():
    """Test the Azure OpenAI API connection"""
    try:
        print("Testing Azure OpenAI Connection...")
        print(f"Endpoint: {AZURE_ENDPOINT}")
        print(f"API Version: {API_VERSION}")
        print(f"Deployment: {DEPLOYMENT_NAME}")
        print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
        print("-" * 50)
        
        # Initialize client
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        
        # Test with a simple prompt
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'Connection successful' if you can read this."}
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print("✅ SUCCESS: Azure OpenAI API connection established!")
        print(f"Response: {result}")
        print(f"Model used: {response.model}")
        print(f"Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print("❌ ERROR: Failed to connect to Azure OpenAI")
        print(f"Error details: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key is correct")
        print("2. Check if the deployment name 'gpt-4o-mini' exists")
        print("3. Ensure the endpoint URL is correct")
        print("4. Verify the API version is supported")
        return False

def test_ai_scoring():
    """Test the AI scoring functionality"""
    try:
        print("\n" + "="*50)
        print("Testing AI Scoring Functionality...")
        
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        
        # Sample job and candidate data
        prompt = """
        Job Requirements:
        - Title: Software Developer
        - Required Experience: 3 years
        - Skills: Python, JavaScript, React
        - Description: Full-stack web development role
        
        Candidate Profile:
        - Experience: 4 years
        - Relevant Experience: Web development with Python and React
        - Skills: Python, JavaScript, React, Node.js
        - Education: Computer Science degree
        - Projects: Built 3 web applications
        
        Rate this candidate's fit for the job on a scale of 1-10. Return only the number.
        """
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.3
        )
        
        score = response.choices[0].message.content.strip()
        print(f"✅ AI Scoring test successful!")
        print(f"Candidate score: {score}/10")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Scoring test failed: {str(e)}")
        return False

def test_interview_questions():
    """Test the interview questions generation"""
    try:
        print("\n" + "="*50)
        print("Testing Interview Questions Generation...")
        
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        
        prompt = """
        Generate 5 interview questions for a Software Developer position requiring Python and React skills.
        Format each question with a number (1-5) and return each question on a new line.
        """
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        
        questions = response.choices[0].message.content.strip()
        print("✅ Interview Questions generation successful!")
        print("Sample questions:")
        print(questions)
        
        return True
        
    except Exception as e:
        print(f"❌ Interview Questions test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Azure OpenAI Configuration Test")
    print("="*50)
    
    # Run all tests
    tests = [
        test_azure_openai_connection,
        test_ai_scoring,
        test_interview_questions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Azure OpenAI configuration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
