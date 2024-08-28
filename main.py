import yt_dlp
import subprocess
import os

def download_bilibili_video(url):
    ydl_opts = {}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        formats = info_dict.get('formats', [])
        audio_formats = [f for f in formats if f.get('acodec') != 'none']
        video_formats = [f for f in formats if f.get('vcodec') != 'none']
        subtitles = info_dict.get('subtitles', {})

        # Display all available audio formats
        print("\nAvailable audio formats:")
        for i, f in enumerate(audio_formats):
            format_id = f.get('format_id', 'unknown')
            ext = f.get('ext', 'unknown')
            tbr = f.get('tbr', 'unknown')
            proto = f.get('protocol', 'unknown')
            
            # Display format information
            print(f"{i}: Format: {ext} - TBR: {tbr} kbps - Protocol: {proto}")

        # Display all available video formats
        print("\nAvailable video formats:")
        for i, f in enumerate(video_formats):
            format_id = f.get('format_id', 'unknown')
            ext = f.get('ext', 'unknown')
            resolution = f.get('resolution') or f.get('height', 'unknown')
            filesize = f.get('filesize', 'unknown')
            filesize_mb = filesize / 1024 / 1024 if isinstance(filesize, int) else 'unknown'
            tbr = f.get('tbr', 'unknown')
            proto = f.get('protocol', 'unknown')
            
            # Display format information
            print(f"{i}: Resolution: {resolution} - Format: {ext} - Filesize: {filesize_mb} MB - TBR: {tbr} kbps - Protocol: {proto}")

        # User selects audio format
        audio_index = int(input("\nEnter the number of the audio format you want to download: "))
        audio_format_id = audio_formats[audio_index].get('format_id')

        # User selects video format
        video_index = int(input("\nEnter the number of the video format you want to download: "))
        video_format_id = video_formats[video_index].get('format_id')

        # Create a directory for the video
        video_title = info_dict.get('title', 'video')
        folder_name = f"{video_title}_files"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Download audio
        ydl_opts['format'] = audio_format_id
        ydl_opts['outtmpl'] = os.path.join(folder_name, 'audio.%(ext)s')  # Output template for audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Download video
        ydl_opts['format'] = video_format_id
        ydl_opts['outtmpl'] = os.path.join(folder_name, 'video.%(ext)s')  # Output template for video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Ask for subtitle download if subtitles are available
        if subtitles:
            print("\nSubtitles are available in the following languages:")
            for i, lang in enumerate(subtitles.keys()):
                print(f"{i}: {lang}")
            download_subtitles = input("\nDo you want to download subtitles? (y/n): ").strip().lower()
            if download_subtitles in ['y', 'yes']:
                subtitle_index = int(input("Enter the number of the subtitle language you want to download: "))
                subtitle_lang = list(subtitles.keys())[subtitle_index]
                ydl_opts['writesubtitles'] = True
                ydl_opts['subtitleslangs'] = [subtitle_lang]
                ydl_opts['outtmpl'] = os.path.join(folder_name, f'subtitles_{subtitle_lang}.%(ext)s')
                print(f"Downloading subtitles to {folder_name}/subtitles_{subtitle_lang}.%(ext)s")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

        # Merge audio and video using FFmpeg
        try:
            audio_file = os.path.join(folder_name, 'audio.m4a')  # Adjust extension based on your audio format
            video_file = os.path.join(folder_name, 'video.mp4')  # Adjust extension based on your video format
            output_file = os.path.join(folder_name, f"{video_title}_final.mp4")
            
            command = [
                'ffmpeg',
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_file
            ]
            subprocess.run(command, check=True)
            print(f"Successfully merged audio and video into {output_file}")

            # Remove the extra audio and video files
            os.remove(audio_file)
            os.remove(video_file)

        except Exception as e:
            print(f"An error occurred during merging: {e}")

if __name__ == "__main__":
    video_url = input("Enter the Bilibili video URL: ")
    download_bilibili_video(video_url)
