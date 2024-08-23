import os
import argparse
from pytubefix import YouTube
from pytubefix.cli import on_progress
from multiprocessing import Pool, cpu_count
import yt_dlp

# Function to download a video
def download_video(outdir, url=None, uid=None):
    assert url or uid, "either URL or ID must be provided"
    
    if uid is not None or "youtube" in url:
        if url is not None:
            uid = url.split('?v=')[-1].strip()
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            ys = yt.streams.get_lowest_resolution()
            ys.download(output_path=outdir, filename=f"{uid}.mp4")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
    else:
        # Set up yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(outdir, '%(id)s.%(ext)s'),  # Save with video title as the filename
            'format': 'best',  # or worst, bestvideo, worstvideo
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

# Function to download a chunk of videos
def download_video_chunk(args):
    outdir, video_urls = args
    for url in video_urls:
        download_video(outdir, url=url)

# Function to divide the video list into chunks and download them in parallel
def download_videos_in_parallel(outdir, video_urls, num_processes):
    chunks = []
    for i in range(num_processes):
        chunks.append(video_urls[i::num_processes])

    # Prepare arguments for each process
    args = [(outdir, chunk) for chunk in chunks]

    # Use multiprocessing to download chunks in parallel
    with Pool(num_processes) as pool:
        pool.map(download_video_chunk, args)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download YouTube videos using multiple processes.")
    parser.add_argument("--num_processes", type=int, default=cpu_count(),
                        help="Number of parallel processes to use for downloading.")
    parser.add_argument("--outdir", type=str, required=True,
                        help="Output directory where the videos will be saved.")
    parser.add_argument("--file", type=str, required=True,
                        help="File containing list of YouTube video URLs, one per line.")

    args = parser.parse_args()

    # Read video URLs from the file
    with open(args.file, 'r') as f:
        video_urls = [line.strip() for line in f if line.strip()]

    # Ensure output directory exists
    os.makedirs(args.outdir, exist_ok=True)

    # Start downloading videos in parallel
    download_videos_in_parallel(args.outdir, video_urls, args.num_processes)

if __name__ == "__main__":
    main()

