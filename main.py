import argparse
import os
from utils.audio import convert_webm_to_wav, transcribe
from utils.common import download_youtube_video, clear_temp_dir, move_to_output
from utils.text import generate_subtitle_file, translate_segments_to
from utils.video import add_subtitles_to_video, crop_video_horizontal_to_vertical, overlay_watermark


def process_video(video_url, languages, watermark_path):
    # Download the video from YouTube
    file_path_webm = download_youtube_video(video_url)

    # Convert the video to WAV format
    file_path_wav = convert_webm_to_wav(file_path_webm)

    # Transcribe the audio to get language and segments
    video_language, segments = transcribe(file_path_wav)

    # Get the base filename and extension
    file_name, _ = os.path.splitext(os.path.basename(file_path_wav))

    # Crop the video horizontally to vertical orientation
    video_vertical = crop_video_horizontal_to_vertical(file_path_webm, f'./temp/horizontal.{video_language}.mp4')

    # Process each language
    for language in languages:
        if video_language != language:
            # Translate segments if the language differs
            translated_segments = translate_segments_to(segments, language)
            subtitle_file = generate_subtitle_file(input_video_name=file_name, language=language,
                                                   segments=translated_segments)
        else:
            # Use original segments if the language matches
            subtitle_file = generate_subtitle_file(input_video_name=file_name, language=language, segments=segments)

        # Add subtitles to the horizontal video
        video_vertical_with_subtitles = add_subtitles_to_video(video_vertical, subtitle_file,
                                                               f'./temp/subtitles.vertical.{language}.mp4')

        # Add subtitles to the full video
        video_with_subtitles = add_subtitles_to_video(file_path_webm, subtitle_file,
                                                      f'./temp/subtitles.full.{language}.mp4')

        # Overlay watermark if provided
        if watermark_path is not None:
            video_vertical_with_watermark = overlay_watermark(video_vertical_with_subtitles, watermark_path,
                                                              f'./temp/{file_name}.vertical.{language}.mp4')
            video_with_watermark = overlay_watermark(video_with_subtitles, watermark_path,
                                                     f'./output/{file_name}.full.{language}.mp4')
            move_to_output(video_vertical_with_watermark, f'./output/{file_name}.vertical.{language}.mp4')
            move_to_output(video_with_watermark, f'./output/{file_name}.full.{language}.mp4')

    # Clean up temporary files
    clear_temp_dir()
    print('Processing complete.')


def main():
    parser = argparse.ArgumentParser(description='Process YouTube video with subtitles and watermark.')
    parser.add_argument('video_url', type=str, help='URL of the YouTube video')
    parser.add_argument('--languages', nargs='+', default=['ru', 'en'],
                        help='Languages for subtitles (default: ru, en)')
    parser.add_argument('--watermark', type=str, default='./static/watermark.jpeg',
                        help='Path to watermark image (default: ./static/watermark.jpeg)')
    args = parser.parse_args()

    # Validate arguments
    if args.video_url is None:
        raise ValueError('Video URL is required.')

    # Call the video processing function
    process_video(args.video_url, args.languages, args.watermark)


if __name__ == '__main__':
    main()
