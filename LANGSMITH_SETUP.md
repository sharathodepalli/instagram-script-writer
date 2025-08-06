# 🔍 LangSmith Integration Setup

## Quick Setup (2 minutes)

### 1. **Get LangSmith API Key**
1. Go to [LangSmith](https://smith.langchain.com)
2. Sign up/Login with your account
3. Go to Settings → API Keys
4. Create a new API key

### 2. **Set Environment Variables**
Add these to your `.env` file:
```bash
# LangSmith Configuration
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Instagram-Script-Writer
```

### 3. **That's It!** 
The integration is already implemented. Just restart the app and you'll see traces in LangSmith.

## 📊 What You'll See in LangSmith

### **Automatic Tracing of:**
- ✅ **User persona creation** - Deep story analysis and pattern learning
- ✅ **Script generation** - Multi-attempt generation with scoring
- ✅ **Quality scoring** - Detailed scoring breakdown
- ✅ **Story analysis** - AI analysis of user backgrounds
- ✅ **All OpenAI API calls** - Costs, latency, tokens used

### **Key Metrics:**
- **Latency** - How long each operation takes
- **Token Usage** - Input/output tokens for cost tracking
- **Success/Error Rates** - System reliability metrics
- **User Interactions** - What users are generating

### **Debugging Power:**
- **Full conversation traces** - See exact prompts and responses
- **Error tracking** - When and why things fail
- **Performance optimization** - Identify bottlenecks
- **User behavior analysis** - Popular topics, patterns

## 📈 Example Traces You'll See

### **User Persona Creation:**
```
🔍 create_user_persona
  ├── 📖 _analyze_user_story
  │   └── 🤖 OpenAI Call (story analysis)
  ├── 🧠 Pattern learning from examples
  └── ✅ Persona created (Alex, marketing expert)
```

### **Script Generation:**
```
🎯 generate_personalized_script  
  ├── 📝 Attempt 1: OpenAI Call → Score: 58.0
  ├── 📝 Attempt 2: OpenAI Call → Score: 64.0  
  ├── 📝 Attempt 3: OpenAI Call → Score: 74.0 ⭐
  ├── 🔍 _score_script_quality
  └── ✅ Best script returned (Score: 74.0)
```

## 🚀 Benefits

### **For Development:**
- **Debug issues faster** - See exactly where things go wrong
- **Optimize performance** - Identify slow operations
- **Track costs** - Monitor OpenAI API usage
- **Improve prompts** - See what works and what doesn't

### **For Business:**
- **User analytics** - What content types are popular
- **Quality metrics** - Track script quality over time
- **Cost monitoring** - Control API expenses
- **Performance tracking** - System reliability

## 🔧 Optional: Advanced Configuration

### **Custom Project Names:**
```bash
LANGCHAIN_PROJECT=My-Script-Writer-v2
```

### **Selective Tracing:**
```python
# Only trace in production
LANGCHAIN_TRACING_V2=true  # Enable
LANGCHAIN_TRACING_V2=false # Disable
```

### **Different Environments:**
```bash
# Development
LANGCHAIN_PROJECT=Script-Writer-Dev

# Production  
LANGCHAIN_PROJECT=Script-Writer-Prod
```

## 📱 Dashboard Access

Once configured, access your traces at:
**https://smith.langchain.com/o/{your-org}/projects/{your-project}**

You'll see:
- **Real-time traces** as users generate scripts
- **Performance metrics** and analytics
- **Cost tracking** for OpenAI usage
- **Error monitoring** and debugging tools

## ⚠️ Note

If you don't set the `LANGCHAIN_API_KEY`, the app will still work perfectly - it just won't send traces to LangSmith. All tracing is optional and doesn't affect core functionality.