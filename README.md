**AI media detection twitter bot**

This bot handles:
- polling the twitter API
- running a YOLOv8 classification model on any media it is tagged in
- replying to the original tweet with:
- - the model's analysis
- - a visualization of what parts of the image are most telling of AI generation (gradCAM)
- i dream of the bot commenting "🤖 AI image" on a political figures tweet (and being correct.. that is rather important too)



**AI generated readme below**



**AI Image Detector Bot**

- **Purpose:**: Detect whether images in Twitter mentions are AI-generated using a YOLOv8 classifier, generate Grad-CAM heatmaps for positive detections, and reply to the tweet with results and optional heatmap media.

- **Language:**: Python 3.12+
- **Key libraries:**: ultralytics (YOLOv8), PyTorch, pytorch-grad-cam, OpenCV, Tweepy, requests

**Quick Start**

- Clone or open the repository in your workspace.
- Create a virtual environment and install dependencies in `requirements.txt`:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

- Put your trained model at `models/ai_detector_run/weights/best.pt` or update `src/config.py` `MODEL_PATH`.

**Configuration**

- Edit `.env` (not in repo) with your Twitter app credentials:
  - `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`, `TWITTER_BEARER_TOKEN`
- `src/config.py` contains runtime options:
  - `TEST_MODE` (True/False) — run the local mock client when True.
  - `CHECK_INTERVAL` — seconds between mention polls.
  - `USE_REAL_REPLY_IN_TEST` and `TEST_TWEET_ID` — when testing, optionally enable sending a real reply to a specific tweet ID (the mock client will prompt for confirmation before posting).

**Run**

- Production (requires valid Twitter credentials and app permissions for read/write):

```bash
python -m main
```

- Test Mode (mock client, no Twitter calls):

```bash
# set TEST_MODE = True in src/config.py
python -m main
```

**Testing real replies safely**

- To test sending a real reply while otherwise in Test Mode:
  - Set `TEST_MODE = True`, `USE_REAL_REPLY_IN_TEST = True`, and set `TEST_TWEET_ID` to the numeric tweet ID you want to reply to in `src/config.py`.
  - When starting, the mock client will prompt for confirmation before initializing the real client and again before sending the reply.
  - Ensure your app in the Twitter Developer Portal has "Read and Write" permissions and regenerate access tokens after changing permissions.

**How it works (high level)**

- `src/bot/handler.py` polls mentions, downloads media, runs `AIDetector.predict_image`, and when label is `ai` generates a Grad-CAM via `src/inference/explainability.py` and replies.
- Grad-CAM expects the model forward to return a Tensor; `ModelWrapper` is used to adapt Ultralytics' model (which can return a tuple) to return the primary tensor for the CAM tool.

**Files of interest**

- `src/bot/handler.py` — main orchestration loop
- `src/bot/twitter_client.py` — real Twitter integration (uses Tweepy)
- `src/bot/mock_twitter_client.py` — mock client for safe local testing
- `src/inference/detector.py` — wrapper around YOLO classifier
- `src/inference/explainability.py` — Grad-CAM logic
- `main.py` — entrypoint

**Troubleshooting & notes**

- If you see `403 Forbidden` when uploading or replying, ensure your app has "Read and Write" permissions and you've regenerated the access tokens.
- To avoid hitting Twitter rate limits, increase `CHECK_INTERVAL` or rely on the mock client for frequent testing.
- If Grad-CAM errors reference tuples or `.cpu()` on a tuple, the `ModelWrapper` fixes the mismatch by returning the first tensor element of the model output.

**Contributing / Extending**

- Add support for videos by extracting representative frames in `src/inference/video_processor.py`.
- Improve mock test fixtures by adding more sample images in `data/single_imgs` or adding JSON fixtures for tweets.

**License**

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
