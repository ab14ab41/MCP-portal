# AI Sandbox - Multi-Provider Testing

The MCP Portal includes a powerful AI Sandbox where you can test your deployed MCP servers with multiple AI providers and models!

## Supported AI Providers

### 1. Anthropic Claude
- **Models**: Opus, Sonnet, Haiku
- **Best for**: Complex reasoning, tool usage, long context
- **Configuration**: API key required

### 2. OpenAI-Compatible APIs
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Azure OpenAI**: Enterprise deployments
- **Local Models**: Ollama, LM Studio, vLLM
- **Configuration**: API key + base URL

## Setup Instructions

### Option 1: Anthropic Claude

1. **Get API Key**
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create a new API key

2. **Configure Backend**
   ```bash
   # Edit backend/.env
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   ```

3. **Restart Services**
   ```bash
   docker-compose restart backend
   ```

### Option 2: OpenAI

1. **Get API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create a new API key

2. **Configure Backend (Optional)**
   ```bash
   # Edit backend/.env
   OPENAI_API_KEY=sk-xxxxx
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

3. **Or Configure in UI**
   - You can also provide API key directly in the AI Sandbox interface
   - Useful for testing different accounts or temporary keys

### Option 3: Local Models (Ollama)

1. **Install Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows: Download from ollama.ai
   ```

2. **Pull a Model**
   ```bash
   ollama pull llama2
   ollama pull mistral
   ```

3. **Configure in UI**
   ```
   Provider: OpenAI
   Model: llama2
   API Key: not-needed
   Base URL: http://host.docker.internal:11434/v1
   ```

## Using the AI Sandbox

### 1. Select MCP Servers

**Single Server Mode:**
- Click one server to use its tools
- Great for focused API testing

**Multi-Server Mode (NEW!):**
- Check multiple servers
- AI can use tools from all selected servers
- Perfect for cross-API workflows

**Example Multi-Server Setup:**
```
✓ GitHub API (12 tools)
  - list_repos, create_issue, get_commit, etc.

✓ Slack API (8 tools)
  - send_message, list_channels, etc.

✓ Stripe API (15 tools)
  - create_payment, list_customers, etc.

Total: 35 tools available to AI
```

### 2. Configure AI Provider

**Anthropic Claude:**
```
Provider: Anthropic Claude
Model: claude-3-5-sonnet-20241022
API Key: (optional - uses backend default)
```

**OpenAI:**
```
Provider: OpenAI
Model: gpt-4o
API Key: sk-proj-xxxxx
Base URL: https://api.openai.com/v1
```

**Local Model:**
```
Provider: OpenAI
Model: llama2
API Key: not-needed
Base URL: http://host.docker.internal:11434/v1
```

### 3. Start Testing

**Simple Queries:**
```
You: "Get user with ID 123"
AI: [Calls get_user(user_id=123)]
AI: "Here's the user information..."
```

**Multi-Tool Workflows:**
```
You: "List all open issues and add a comment to each"
AI: [Calls list_issues(state="open")]
AI: [Calls add_comment(issue_id=...) for each]
AI: "I've added comments to 5 open issues..."
```

**Cross-API Workflows:**
```
You: "When someone stars my repo, thank them in Slack"
AI: [Calls github_list_stargazers]
AI: [Calls slack_send_message for each new star]
AI: "I've sent thank you messages to 3 new stargazers..."
```

## Features

### Real-Time Chat
- Interactive conversation interface
- Full context maintained across messages
- Markdown formatting support

### Tool Execution
- **Automatic Execution**: AI decides which tools to use
- **Visual Feedback**: See tool calls with parameters
- **Result Display**: View API responses
- **Error Handling**: Clear error messages

### Multi-MCP Support
- Select multiple deployed servers
- Tools combined from all servers
- Seamless cross-API interactions
- Search servers by name

### Provider Flexibility
- Switch between Anthropic and OpenAI
- Override default API keys
- Custom model selection
- Local model support

### Monitoring
- **Token Usage**: Track input/output tokens
- **Latency**: See response times
- **Tool Calls**: Count and visualize tool usage
- **Conversation History**: Review past interactions

## Advanced Usage

### Testing API Workflows

**Scenario: E-commerce Order Processing**
```
Selected MCPs:
✓ Payment API (Stripe)
✓ Inventory API
✓ Notification API (Twilio)

Query: "Process order #123: charge customer, update inventory, send SMS"

AI will:
1. Call stripe_create_charge
2. Call inventory_decrease_stock
3. Call twilio_send_sms
4. Return success confirmation
```

### Comparing AI Providers

**Test with Claude:**
- Better at complex multi-step workflows
- Excellent tool usage
- Higher cost but better quality

**Test with GPT-4:**
- Good balance of cost and performance
- Fast responses
- Wide availability

**Test with Local Models:**
- No API costs
- Full privacy
- May need prompt tuning

### Custom Tool Descriptions

When configuring endpoints, write AI-friendly descriptions:

**❌ Bad:**
```
"Gets user"
```

**✅ Good:**
```
"Retrieve detailed user profile including email, name, preferences, and account status. Use this when you need complete user information."
```

## Troubleshooting

### Provider Issues

**Anthropic Errors:**
- Check API key in `backend/.env`
- Verify key has credits
- Try overriding key in UI

**OpenAI Errors:**
- Verify base URL includes `/v1`
- Check model name is correct
- Test with curl first

**Local Model Issues:**
- Ensure Ollama is running
- Use `host.docker.internal` not `localhost`
- Pull model first: `ollama pull llama2`

### Tool Execution Failures

**Timeout Errors:**
- Target API may be slow
- Check network connectivity
- Increase timeout in MCP server

**Authentication Errors:**
- Verify API base URL is correct
- Check API authentication
- Review MCP server logs

**Invalid Parameters:**
- Check parameter configurations
- Verify mandatory parameters are set correctly
- Review tool descriptions for clarity

### Multi-Server Issues

**Tools Not Combining:**
- Refresh the page
- Verify all servers are active
- Check deployment status

**Duplicate Tool Names:**
- Rename tools in endpoint configuration
- Use unique, descriptive names
- Avoid generic names like "get" or "list"

## Best Practices

### 1. Tool Descriptions
- Be specific and detailed
- Include examples
- Mention when to use the tool

### 2. Parameter Configuration
- Mark truly required parameters as mandatory
- Provide clear parameter descriptions
- Use appropriate types

### 3. Multi-MCP Testing
- Start with single MCPs
- Test each MCP individually first
- Combine related APIs

### 4. Provider Selection
- Use Claude for complex workflows
- Use GPT-4 for cost-effective testing
- Use local models for privacy-sensitive testing

### 5. Monitoring
- Track token usage
- Watch for rate limits
- Review tool call patterns

## Examples

### Example 1: GitHub Repository Analysis

```
Selected MCP: GitHub API

Query: "Analyze my top repository: show stars, recent commits, and open issues"

Tool Calls:
1. list_repositories(sort="stars", limit=1)
2. get_repository_stats(repo_id=...)
3. list_commits(repo_id=..., limit=5)
4. list_issues(repo_id=..., state="open")

Response:
"Your top repository 'awesome-project' has 1,234 stars.
Recent commits show active development with 5 commits this week.
There are 12 open issues, mostly feature requests..."
```

### Example 2: Cross-API Workflow

```
Selected MCPs:
✓ GitHub API
✓ Slack API

Query: "Monitor my repo and notify #dev channel when new issues are created"

Tool Calls:
1. github_list_issues(state="open", since="1h")
2. slack_send_message(channel="#dev", text="New issue: ...")

Response:
"I've checked for new issues in the last hour and found 2 new ones.
I've sent notifications to #dev channel for both issues."
```

### Example 3: Local Model Testing

```
Provider: Ollama (llama2)
Selected MCP: Simple API

Query: "Get user 123"

Note: May require more explicit instructions:
"Use the get_user tool with user_id=123"

Local models may need:
- More explicit instructions
- Simpler queries
- Retry with different prompts
```

## Resources

- **Anthropic Docs**: https://docs.anthropic.com/
- **OpenAI Docs**: https://platform.openai.com/docs
- **Ollama**: https://ollama.ai/
- **MCP Protocol**: https://modelcontextprotocol.io/

## Need Help?

- Check the [main documentation](DOCUMENTATION.md)
- Review [troubleshooting guide](DOCUMENTATION.md#troubleshooting)
- Open an [issue on GitHub](https://github.com/yourusername/mcp-portal/issues)
