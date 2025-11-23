# API Key Setup Guide

## Getting Your OpenAI API Key

### Step 1: Create OpenAI Account

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Click "Sign up" if you don't have an account
3. Verify your email address
4. Complete the registration process

### Step 2: Set Up Billing

**Important**: You need billing configured to use the API

1. Go to [Billing Settings](https://platform.openai.com/account/billing/overview)
2. Click "Add payment method"
3. Add a credit card or payment method
4. Set up usage limits (recommended: $5-10 monthly limit)

### Step 3: Generate API Key

1. Navigate to [API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give it a name (e.g., "Spanish Conjugation GUI")
4. **Important**: Copy the key immediately - you won't see it again!
5. Store it safely (the app will help with this)

## Setting Up the API Key

### Method 1: Setup Wizard (Recommended)

1. Launch the Spanish Conjugation GUI
2. The setup wizard will appear automatically on first run
3. Follow the steps to configure your API key securely
4. The wizard will test your key and guide you through any issues

### Method 2: Manual Environment Variable

Create a `.env` file in the application directory:

```bash
# .env file
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Method 3: System Environment Variable

**Windows:**
```cmd
setx OPENAI_API_KEY "sk-your-actual-api-key-here"
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
# Add to ~/.bashrc or ~/.zshrc to make permanent
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
```

### Method 4: Security Settings (After First Run)

1. Open the application
2. Click the 🔐 Security Settings button in the toolbar
3. Go to the "API Keys" tab
4. Click "Change API Key"
5. Enter your new key

## Verifying Your Setup

### Test in the Application

1. Launch the app
2. Go to Security Settings → API Keys
3. Click "Test API Key"
4. You should see: ✅ API key test successful!

### Check Your Usage

Monitor your API usage:
1. Visit [OpenAI Usage Dashboard](https://platform.openai.com/account/usage)
2. Check your current usage and limits
3. Set up usage alerts if desired

## Cost Information

### Typical Usage Costs

The Spanish Conjugation GUI is designed to be cost-effective:

- **Exercise Generation**: ~$0.001-0.002 per batch (5 exercises)
- **Explanations**: ~$0.0005-0.001 per explanation
- **Hints**: ~$0.0003-0.0005 per hint
- **Monthly Estimate**: $1-5 for regular use (50-200 exercises/month)

### Cost-Saving Tips

1. **Use Offline Mode** - Enable for basic practice without API calls
2. **Batch Exercises** - Generate multiple exercises at once
3. **Cache Settings** - Enable exercise caching to reuse content
4. **Set Usage Limits** - Configure monthly spending limits on OpenAI platform

## Troubleshooting

### "Invalid API Key" Error

**Check the key format:**
- Should start with `sk-`
- Should be 51 characters long
- No spaces or line breaks

**Common fixes:**
- Copy the key again from OpenAI platform
- Check for extra characters or spaces
- Ensure you're using the correct key (not organization ID)

### "Rate Limit" Error

**Causes:**
- Making requests too quickly
- Exceeded usage quota
- Free tier limitations

**Solutions:**
- Wait a few minutes and try again
- Check your usage on OpenAI platform
- Upgrade to paid tier if on free tier

### "Insufficient Quota" Error

**This means:**
- You've used up your available credits
- Your payment method was declined
- Your usage limit was reached

**Solutions:**
- Add funds to your OpenAI account
- Check your payment method
- Increase your usage limits

### "Authentication Failed" Error

**Possible causes:**
- API key is incorrect or expired
- Key was deleted or revoked
- Account issues

**Solutions:**
- Generate a new API key
- Check account status
- Verify billing information

## Security Best Practices

### Protecting Your API Key

1. **Never share your API key**
2. **Don't commit it to version control**
3. **Use environment variables or secure storage**
4. **Rotate keys periodically**
5. **Monitor usage regularly**

### If Your Key is Compromised

1. **Immediately revoke the key** on OpenAI platform
2. **Generate a new key**
3. **Update your configuration**
4. **Check usage for unauthorized activity**
5. **Consider changing your OpenAI password**

## Alternative Providers (Coming Soon)

Future versions will support:

- **Anthropic Claude** - Alternative AI provider
- **Google Gemini** - Google's AI models  
- **Local Models** - Run AI models locally
- **Azure OpenAI** - Enterprise OpenAI service

## Offline Mode

Don't want to use an API key? Enable offline mode:

1. Launch the app
2. Go to Settings
3. Enable "Offline Mode"
4. Practice with built-in exercises

**Offline mode limitations:**
- Pre-built exercises only
- No AI-generated content
- No personalized explanations
- Limited exercise variety

## Getting Help

### Resources

- [OpenAI Documentation](https://platform.openai.com/docs)
- [OpenAI Community Forum](https://community.openai.com/)
- [API Status Page](https://status.openai.com/)

### Application Support

If you have issues with the Spanish Conjugation GUI:

1. Check this documentation first
2. Enable debug logging
3. Check the troubleshooting section
4. File an issue with error details

### Common Questions

**Q: How much will this cost me?**
A: Typically $1-5/month for regular use. Monitor your usage on the OpenAI platform.

**Q: Can I use a free API key?**
A: OpenAI no longer offers free API access. You need a paid account with billing set up.

**Q: Is my API key safe?**
A: Yes, the app uses secure storage (system keyring or encryption) to protect your key.

**Q: Can I use multiple API keys?**
A: Currently, one key at a time is supported. Future versions may support multiple providers.

**Q: What happens if I run out of credits?**
A: The app will show an error and switch to offline mode until you add more credits.

---

**Need more help?** Check the main documentation or file an issue on the project repository.