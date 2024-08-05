from dataclasses import dataclass
from os.path import join
from googletrans import Translator
from typing import List, Union, Dict
from utils.common import format_time

def generate_subtitle_file(input_video_name, language, segments, output_dir='./temp'):
    """
    Generates a subtitle file in SRT format for given segments and language.
    Args:
        input_video_name (str): Name of the input video.
        language (str): Target language for subtitles.
        segments (List): List of segments to include in the subtitle file.
        output_dir (str): Directory to save the generated subtitle file.
    Returns:
        str: Path to the generated subtitle file.
    """
    subtitle_file = join(output_dir, f"{input_video_name}.{language}.srt")
    with open(subtitle_file, "w", encoding="utf-8") as f:
        for index, segment in enumerate(segments):
            segment_start = format_time(segment['start'] if isinstance(segment, dict) else segment.start)
            segment_end = format_time(segment['end'] if isinstance(segment, dict) else segment.end)
            segment_text = segment['text'] if isinstance(segment, dict) else segment.text
            f.write(f"{index + 1}\n")
            f.write(f"{segment_start} --> {segment_end}\n")
            f.write(f"{segment_text}\n\n")
    return subtitle_file

@dataclass
class TranslatedSegment:
    start: float
    end: float
    text: str

def translate_segments_to(segments: List[Union[Dict, TranslatedSegment]], language: str) -> List[TranslatedSegment]:
    """
    Translates a list of segments to the target language using Google Translate.
    Args:
        segments (List[Union[Dict, TranslatedSegment]]): List of segments to translate.
        language (str): Target language for translation.
    Returns:
        List[TranslatedSegment]: List of translated segments.
    """
    translator = Translator()
    translated_segments = []
    for segment in segments:
        if isinstance(segment, dict):
            original_text = segment['text']
            start = segment['start']
            end = segment['end']
        else:
            original_text = segment.text
            start = segment.start
            end = segment.end
        
        translated_text = translator.translate(original_text, dest=language).text
        translated_segment = TranslatedSegment(start=start, end=end, text=translated_text)
        translated_segments.append(translated_segment)
    return translated_segments

def translate_to(text: str, language: str) -> str:
    return Translator().translate(text, dest=language).text