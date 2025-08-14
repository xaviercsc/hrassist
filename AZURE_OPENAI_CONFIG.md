# Azure OpenAI Configuration Summary

## Configuration Details

### Azure OpenAI Service
- **API Key**: your-azure-openai-api-key
- **Endpoint**: https://your-openai-resource.openai.azure.com
- **API Version**: 2025-01-01-preview

### Model Deployment
- **Deployment Name**: gpt-4o-mini
- **Model Name**: gpt-4o-mini
- **Model Version**: 2024-07-18

### Rate Limits
- **Tokens per minute**: 250,000
- **Requests per minute**: 2,500

### Complete Endpoint URL
```
https://your-openai-resource.openai.azure.com
```

## Usage in Application

The HR Assist AI application uses Azure OpenAI for:

1. **Candidate Scoring**: AI evaluates candidate fit for job positions (1-10 scale)
2. **Interview Questions**: Generates 15 customized interview questions based on:
   - 5 technical questions specific to required skills
   - 5 behavioral/situational questions
   - 3 questions about experience and projects
   - 2 questions about cultural fit and motivation

## Testing

Run the test script to verify your configuration:
```bash
python test_azure_openai.py
```

This will test:
- ✅ API connection
- ✅ AI scoring functionality
- ✅ Interview questions generation

## Environment Variables

The application loads configuration from `.env` file:
```
OPENAI_API_KEY=xxxxxxxxxxxxxxxxx
HR_ADMIN_SECRET_CODE=QWERTY
SECRET_KEY=your-secret-key-change-in-production
```

## Error Handling

The application includes fallback mechanisms:
- If Azure OpenAI is unavailable, it uses local scoring algorithms
- Provides default interview questions when AI generation fails
- Detailed error logging for troubleshooting

## Security Notes

- API key is loaded from environment variables
- Never commit API keys to version control
- Use `.gitignore` to exclude `.env` file
- API key is partially masked in logs for security
