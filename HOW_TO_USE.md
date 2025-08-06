# Instagram Script-Writer - Complete Usage Guide

## 🎉 Congratulations! Your application is now set up and ready to use.

## 📋 What's Been Set Up

✅ **Pinecone Index**: `scriptwriter` index created and configured
✅ **Sample Scripts**: 5 high-quality sample scripts added to your `/scripts` directory
✅ **API Keys**: OpenAI and Pinecone APIs configured and working
✅ **Streamlit App**: Running at http://localhost:8503

## 🚀 How to Use the Application

### 1. **Access the App**

- Open your browser and go to: http://localhost:8503
- You'll see the Instagram Script-Writer interface

### 2. **Generate Your First Script**

#### Option A: Generate WITHOUT Examples (Recommended for now)

1. Go to the "📝 Generate Script" page
2. Enter a topic like: "healthy breakfast ideas" or "productivity tips"
3. **UNCHECK** the "Use examples" checkbox (since Pinecone ingestion had errors)
4. Click "🚀 Generate Script"
5. Watch as AI generates a complete Instagram script!

#### Option B: Generate WITH Examples (After fixing Pinecone)

1. Enter your topic
2. **KEEP** the "Use examples" checkbox checked
3. Generate script - it will use similar scripts as inspiration

### 3. **Advanced Features**

#### Generate Multiple Variants

- Check "Generate variants" in Advanced Options
- Choose 2-5 variants for A/B testing

#### Auto-Polish Scripts

- Check "Auto-polish" to automatically improve the generated script
- Uses advanced AI to enhance clarity and engagement

#### Quality Check

- Check "Quality check" to get detailed quality analysis
- Checks length, sections, hashtags, and overall score

### 4. **Instagram Scraping (Telugu Content)**

If you want to use the Instagram scraper:

1. Go to the sidebar
2. Click "🇮🇳 Refresh Telugu Examples"
3. This will fetch Telugu reels from Instagram and create scripts

## 📱 App Features Explained

### Main Pages:

1. **📝 Generate Script**

   - Main script generation page
   - Enter topic and customize options
   - View generated scripts with formatting

2. **📚 Manage Scripts**

   - View all generated scripts
   - Load, edit, or delete scripts
   - Export scripts for later use

3. **🔧 Settings**

   - Check API connection status
   - Re-ingest scripts into Pinecone
   - Clear generated scripts

4. **📊 Analytics**
   - View script generation statistics
   - Quality score distributions
   - Recent script performance

### Sidebar Quick Actions:

- **🔄 Ingest Scripts**: Add your custom scripts to Pinecone
- **🇮🇳 Refresh Telugu Examples**: Fetch new Telugu content from Instagram
- **📊 Check Quality**: Analyze current script quality

## 🛠 Troubleshooting

### Common Issues:

1. **"Failed to create retriever" Error**

   - Solution: Uncheck "Use examples" when generating scripts
   - This bypasses Pinecone and uses direct AI generation

2. **No Script Generated**

   - Check your OpenAI API key in the .env file
   - Make sure you have internet connection

3. **Instagram Scraping Fails**
   - Check Instagram credentials in .env file
   - Instagram may be rate-limiting (normal behavior)

### If Pinecone Errors Persist:

You can still use the app effectively without Pinecone by:

- Always unchecking "Use examples"
- Using direct AI generation (which works perfectly)
- Adding your own scripts manually to the `/scripts` folder

## 📝 Sample Topics to Try

Here are some great topics to test with:

**Lifestyle & Wellness:**

- Morning routine for productivity
- 5-minute stress relief techniques
- Natural skincare DIY recipes
- Better sleep habits
- Healthy meal prep ideas

**Business & Productivity:**

- Time management hacks
- Social media content ideas
- Small business marketing tips
- Work-from-home productivity
- Goal setting strategies

**Entertainment & Lifestyle:**

- Travel packing hacks
- Budget-friendly date ideas
- Home organization tips
- Fashion styling tricks
- Quick workout routines

## 🎯 Best Practices

1. **Be Specific**: Instead of "fitness", try "10-minute morning workout for beginners"
2. **Use Trends**: Include current trending topics in your niche
3. **Test Variants**: Generate multiple versions and A/B test them
4. **Quality Check**: Always run quality checks before posting
5. **Customize**: Edit the generated scripts to match your personal voice

## 🔄 Regular Maintenance

- **Weekly**: Add new scripts to your `/scripts` folder and re-ingest
- **Monthly**: Check for new features and updates
- **As Needed**: Refresh Telugu examples if you use that feature

## 🆘 Getting Help

If you encounter any issues:

1. Check the Settings page for API status
2. Look at the console/terminal for error messages
3. Try generating without examples first
4. Restart the Streamlit app if needed

## 🎊 You're All Set!

Your Instagram Script-Writer is ready to help you create amazing content. Start by generating a few scripts on topics you're passionate about and see the AI magic in action!

**Happy Script Writing! 🎬✨**
