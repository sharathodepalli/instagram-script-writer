# Top Telugu Reels Scraper Specification

**Goal:** Fetch the highest-performing public Telugu Instagram Reels and convert them into script templates.

### 1. JSON Schema for each reel (saved as `data/raw_reels/Telugu/<shortcode>.json`):

```json
{
  "id":       <integer>,      // Instagram internal media ID
  "shortcode": "<string>",    // unique post code
  "views":    <integer>,      // number of video views
  "likes":    <integer>,      // number of likes
  "comments": <integer>,      // number of comments
  "caption":  "<string>",     // full caption text
  "audio":    "<string>"      // audio title or snippet name
}
```

### 2. Processing steps

1. **Fetch** up to `MAX_FETCH` reels under `#Telugu` with Instaloader.
2. **Save** each reel's metadata as above.
3. **Load** all JSON, sort by `views` descending, take top-N (default 20).
4. **Write** summary `data/top_reels.csv` with columns: `shortcode,views,likes,comments,caption,audio`.
5. **Generate** a script template for each top reel in `scripts/auto_telugu/` using our existing script fields:

   ```
   TITLE: Telugu Reel <shortcode>
   FORMAT: Reel

   HOOK:
   <Use first line of caption or craft a punchy Telugu hook.>

   BODY:
   - Original audio: "<audio>"
   - Visual: mirror pacing of key scene.
   - Narration: summarize action.

   CTA:
   "Follow for more Telugu trends!"

   CAPTION:
   <trimmed original caption ≤120 chars>

   HASHTAGS:
   #Telugu #Trending #Reels #TeluguReels #InstaTelugu

   VISUAL_DIRECTIONS:
   - replicate camera angles & transitions.
   ```
