#!/usr/bin/env python3
"""
Audio Transcription Utility using Google AI (Gemini)
Transcribes audio files to text using Gemini 2.5 Pro or 2.0 Flash models
"""

import os
import sys
import base64
import logging
import argparse
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model options (same as Telegram bot)
MODEL_OPTIONS = {
    'flash': 'models/gemini-2.0-flash-exp',
    'pro': 'models/gemini-2.5-pro-exp-03-25'
}

DEFAULT_MODEL = 'flash'

# Transcription prompt (same as Telegram bot)
TRANSCRIPTION_PROMPT = """Transcribe this audio exactly in its original language. Keep length. Add paragraph spacing. Remove filler. Fix typos.

If there are multiple speakers, identify and label them as 'Speaker 1:', 'Speaker 2:', etc.

Do not include any headers, titles, or additional text - only the transcription itself. NO MARKDOWN FORMATTING!!!

When transcribing, add line breaks between different paragraphs or distinct segments of speech to improve readability."""

# Supported audio MIME types
SUPPORTED_AUDIO_TYPES = {
    'audio/mpeg',       # .mp3
    'audio/wav',        # .wav
    'audio/ogg',        # .ogg
    'audio/x-m4a',      # .m4a
    'audio/mp4',        # .mp4 audio
    'audio/x-wav',      # alternative wav
    'audio/webm',       # .webm
    'audio/aac',        # .aac
    'audio/x-aac',      # alternative aac
    'video/mp4',        # .mp4 files (some contain audio)
    'application/octet-stream',  # Some files come with this generic type
}

# File extension to MIME type mapping for Gemini API
AUDIO_EXTENSIONS_TO_MIME = {
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav', 
    '.ogg': 'audio/ogg',
    '.m4a': 'audio/mp4',
    '.mp4': 'audio/mp4',
    '.aac': 'audio/aac',
    '.webm': 'audio/webm'
}

def get_api_key():
    """Get Google AI API key from environment"""
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY not found in environment variables. Please set it in .env file.")
    return api_key

def get_gemini_mime_type(file_path):
    """Get the appropriate MIME type for Gemini API based on file extension"""
    file_ext = Path(file_path).suffix.lower()
    return AUDIO_EXTENSIONS_TO_MIME.get(file_ext, 'audio/mp4')

def is_audio_file(file_path):
    """Check if a file is an audio file based on file extension"""
    file_ext = Path(file_path).suffix.lower()
    return file_ext in AUDIO_EXTENSIONS_TO_MIME

def generate_descriptive_filename(transcript_text, original_filename):
    """Generate a descriptive filename based on transcript content"""
    # Clean the transcript text
    text = transcript_text.strip()
    
    # Take first 100 characters and clean them
    preview = text[:100].replace('\n', ' ').replace('\r', ' ')
    
    # Remove speaker labels for filename generation
    preview = re.sub(r'Speaker \d+:\s*', '', preview)
    
    # Extract meaningful words (remove common words)
    words = re.findall(r'\b[A-Za-z]{3,}\b', preview)
    common_words = {'the', 'and', 'are', 'you', 'for', 'not', 'with', 'have', 'this', 'that', 'was', 'but', 'they', 'been', 'have', 'their', 'said', 'each', 'which', 'she', 'how', 'will', 'can', 'what', 'when', 'where', 'who', 'why', 'would', 'could', 'should', 'about', 'from', 'into', 'over', 'after', 'before', 'during', 'through', 'above', 'below', 'between', 'among'}
    
    meaningful_words = [word.lower() for word in words if word.lower() not in common_words]
    
    # Take first 3-5 meaningful words
    if meaningful_words:
        desc_words = meaningful_words[:4]
        description = '_'.join(desc_words)
    else:
        # Fallback to first few words
        first_words = text.split()[:3]
        description = '_'.join(word.lower() for word in first_words if word.isalpha())
    
    # Clean description
    description = re.sub(r'[^\w\s-]', '', description)
    description = re.sub(r'[-\s]+', '_', description)
    
    # Limit length
    if len(description) > 50:
        description = description[:50]
    
    # Fallback if description is empty
    if not description:
        description = "transcript"
    
    # Add timestamp and original filename info
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = Path(original_filename).stem
    
    return f"{description}_{original_name}_{timestamp}.md"

async def transcribe_audio(audio_path, model_key='flash'):
    """
    Transcribe audio file using Gemini API
    """
    try:
        # Validate file
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not is_audio_file(audio_path):
            raise ValueError(f"File is not a supported audio format: {audio_path}")
        
        # Get model
        model_name = MODEL_OPTIONS.get(model_key, MODEL_OPTIONS[DEFAULT_MODEL])
        logger.info(f"Using model: {model_name}")
        
        # Read audio file
        with open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        logger.info(f"Loaded audio file: {audio_path} ({len(audio_data)} bytes)")
        
        # Get MIME type
        mime_type = get_gemini_mime_type(audio_path)
        logger.info(f"MIME type: {mime_type}")
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Initialize Gemini
        genai.configure(api_key=get_api_key())
        
        # Create the model with safety settings
        model = genai.GenerativeModel(
            model_name, 
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        )
        
        # Prepare the content for Gemini
        content_parts = [
            {"text": TRANSCRIPTION_PROMPT},
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": audio_base64
                }
            }
        ]
        
        logger.info("Sending to Gemini for transcription...")
        
        # Generate the transcription
        response = model.generate_content(content_parts)
        
        # Check if response is blocked due to safety filters
        if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
            logger.warning("Response was blocked or empty. Checking safety ratings.")
            if response.candidates and response.candidates[0].safety_ratings:
                for rating in response.candidates[0].safety_ratings:
                    logger.warning(f"Safety rating: {rating.category}: {rating.probability}")
            raise ValueError("Transcription was blocked due to content restrictions or the audio format is not supported.")
        
        # Get transcript text safely
        try:
            transcript = response.text
        except ValueError as e:
            logger.warning(f"Error accessing response.text: {str(e)}")
            # Fallback to manually extracting text
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        transcript = part.text
                        break
                else:
                    raise ValueError("Could not extract transcription from response.")
            else:
                raise ValueError("Transcription response was empty or blocked.")
        
        # Clean up transcript (remove headers that might be added despite prompt)
        transcript = transcript.replace("# Transcription\n\n", "")
        transcript = transcript.replace("Okay, here is the transcription:\n", "")
        transcript = transcript.replace("Here's the transcription:\n", "")
        transcript = transcript.strip()
        
        # Count speaker labels
        speaker_labels = set()
        for line in transcript.split('\n'):
            if line.strip().startswith(('Speaker ', '**Speaker ')):
                for i in range(1, 10):
                    if f"Speaker {i}:" in line or f"**Speaker {i}:**" in line:
                        speaker_labels.add(i)
        
        logger.info(f"Speakers detected: {len(speaker_labels)}")
        
        # Only remove speaker labels if there's exactly one speaker
        if len(speaker_labels) == 1:
            transcript = transcript.replace("**Speaker 1:**", "")
            transcript = transcript.replace("Speaker 1:", "")
            transcript = transcript.strip()
        
        return transcript
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise

def save_transcript(transcript, original_audio_path, output_dir):
    """Save transcript to markdown file with descriptive filename"""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate descriptive filename
        filename = generate_descriptive_filename(transcript, original_audio_path)
        output_file = output_path / filename
        
        # Create transcript content
        transcript_content = f"""# Audio Transcript

**Source File:** {Path(original_audio_path).name}  
**Transcribed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**File Size:** {Path(original_audio_path).stat().st_size / (1024*1024):.2f} MB

---

{transcript}

---

*Transcribed using Google AI Gemini*
"""
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript_content)
        
        logger.info(f"Transcript saved to: {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Error saving transcript: {str(e)}")
        raise

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Transcribe audio files using Google AI Gemini')
    parser.add_argument('audio_file', help='Path to audio file to transcribe')
    parser.add_argument('--model', choices=['flash', 'pro'], default='flash', 
                        help='AI model to use (default: flash)')
    parser.add_argument('--output', default='transcripts', 
                        help='Output directory for transcripts (default: transcripts)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        print(f"🎙️  Audio Transcription Tool")
        print(f"=" * 50)
        print(f"📁 Input file: {args.audio_file}")
        print(f"🤖 Model: {MODEL_OPTIONS[args.model]}")
        print(f"📂 Output directory: {args.output}")
        print()
        
        # Check if file exists
        if not Path(args.audio_file).exists():
            print(f"❌ Error: Audio file not found: {args.audio_file}")
            return 1
        
        # Check if it's an audio file
        if not is_audio_file(args.audio_file):
            print(f"❌ Error: File is not a supported audio format.")
            print(f"Supported formats: {', '.join(AUDIO_EXTENSIONS_TO_MIME.keys())}")
            return 1
        
        print("🔄 Transcribing audio (this may take a while)...")
        
        # Transcribe audio
        import asyncio
        transcript = asyncio.run(transcribe_audio(args.audio_file, args.model))
        
        # Save transcript
        output_file = save_transcript(transcript, args.audio_file, args.output)
        
        print("✅ Transcription completed successfully!")
        print(f"📄 Transcript saved to: {output_file}")
        
        # Show preview
        print(f"\n📝 Preview (first 200 characters):")
        print("-" * 50)
        preview = transcript[:200] + "..." if len(transcript) > 200 else transcript
        print(preview)
        print("-" * 50)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
