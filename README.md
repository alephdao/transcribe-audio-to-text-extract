# Audio Transcription Utility

A Python utility to transcribe audio files to text using Google AI Gemini models (2.5 Pro or 2.0 Flash).

## Features

- 🎙️ Transcribe various audio formats (MP3, WAV, M4A, AAC, OGG, WEBM, MP4)
- 🤖 Choose between Gemini 2.5 Pro (high accuracy) or 2.0 Flash (fast)
- 📝 Smart filename generation based on content
- 👥 Multi-speaker detection and labeling
- 📂 Organized output in markdown format
- 🔒 Secure API key management

## Installation

1. **Clone/Navigate to the directory:**
   ```bash
   cd /Users/philip.galebach/coding-projects/utilities/transcribe-audio-to-text-extract
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` (or use existing `.env`)
   - Add your Google AI API key to `.env`

## Usage

### Basic Usage
```bash
python transcribe_audio.py path/to/audio.mp3
```

### Advanced Usage
```bash
# Use Gemini 2.5 Pro model (higher accuracy)
python transcribe_audio.py audio.mp3 --model pro

# Custom output directory
python transcribe_audio.py audio.mp3 --output ./my-transcripts

# Verbose logging
python transcribe_audio.py audio.mp3 --verbose
```

### Help
```bash
python transcribe_audio.py --help
```

## Supported Audio Formats

- **MP3** (.mp3)
- **WAV** (.wav)
- **M4A** (.m4a)
- **AAC** (.aac)
- **OGG** (.ogg)
- **WEBM** (.webm)
- **MP4** (.mp4) - audio content

## Output Format

Transcripts are saved as Markdown files in the `transcripts/` directory with descriptive filenames based on content:

```
meeting_discussion_agenda_20250623_141530.md
lecture_physics_quantum_20250623_142000.md
```

Each transcript includes:
- Source file information
- Transcription timestamp
- File size
- Clean transcript text
- Speaker labels (when multiple speakers detected)

## Configuration

### Environment Variables (.env)
```bash
GOOGLE_AI_API_KEY=your_gemini_api_key_here
```

### Model Options
- **flash** (default): Gemini 2.0 Flash - Fast and efficient
- **pro**: Gemini 2.5 Pro - Higher accuracy, slower processing

## API Key Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
   ```bash
   GOOGLE_AI_API_KEY=your_api_key_here
   ```

## Example Output

```markdown
# Audio Transcript

**Source File:** meeting_recording.mp3  
**Transcribed:** 2025-06-23 14:15:30  
**File Size:** 18.27 MB

---

Welcome everyone to today's quarterly review meeting. Let's start by going through the agenda.

Speaker 1: The sales numbers look really promising this quarter.

Speaker 2: I agree, but we should also focus on customer retention metrics. They're equally important for long-term growth.

Speaker 1: That's a great point. Let's dive into those numbers next.

---

*Transcribed using Google AI Gemini*
```

## Error Handling

The utility handles common errors gracefully:
- Missing API key
- Unsupported file formats
- Network issues
- Content safety restrictions
- File not found errors

## Development

### Project Structure
```
transcribe-audio-to-text-extract/
├── transcribe_audio.py     # Main script
├── requirements.txt        # Dependencies
├── .env                   # Environment variables (git ignored)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── transcripts/          # Output directory (git ignored)
└── venv/                 # Virtual environment (git ignored)
```

### Dependencies
- `google-generativeai` - Google AI Gemini API
- `python-dotenv` - Environment variable management

## Troubleshooting

**"GOOGLE_AI_API_KEY not found"**
- Ensure `.env` file exists with your API key
- Check that the virtual environment is activated

**"File is not a supported audio format"**
- Check that your file has a supported extension
- Supported: .mp3, .wav, .m4a, .aac, .ogg, .webm, .mp4

**"Transcription was blocked"**
- Content may have been flagged by safety filters
- Try with a different audio file

## License

This project is open source and available under the MIT License.

---

*Built with Google AI Gemini for accurate audio transcription*
