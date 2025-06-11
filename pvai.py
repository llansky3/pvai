import sys
import time
import yaml
import argparse

from google import genai

class GeminiAPI:
    def __init__(self, model):
        api_key = self.get_secret_api_key()
        self.client = genai.Client(api_key=api_key)
        self.available_models = self.list_generate_content_models()
        if model not in self.available_models:
            raise ValueError(
                f'Model {model} is not supported. Available models are: {self.available_models}!'
            )
        else:
            self.model = model

    def list_generate_content_models(self):
        models = []
        for m in self.client.models.list():
            for action in m.supported_actions:
                if action == "generateContent":
                    models.append(m.name)
        models = [m.replace('models/', '') for m in models]
        return models

    def generate_content(self, query):
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=query
            )
            return response.text
        except Exception as e:
            return f'Something went wrong with Gemini API call: {e}'

    def get_secret_api_key(secret):
        """
        Secrets shall be stored in separate secrets.yml file containing:
        SECRETS:
          - gemini_api_key: YOUR_API_KEY HERE
        """
        secret = 'gemini_api_key'
        with open('secrets.yml', 'r') as file:
            data = yaml.safe_load(file)
        for d in data['SECRETS']:
            if secret in d:
                return d[secret]
        return None

def pvai(api, args, chunk_size=4096):
    """
    This functions mimics pv utility in term of reading from stdin, and writing to stdout.
    But it uses stderr to print AI thoughts in stderr.
    
    Optional mode if args.follow == True:
        Continuously print AI thoughts as the data are coming in from stdin.
        Otherwise gather the data first and share the thoughts at the end.
    """

    prompt = """
        The below text after ### is a data stream likely coming from a standard output of a Linux shall command. 
        Could you comments what it likely, what problems or normal operation you see and generally just share your thoughts on it. 
        ###
        """    
    if not args.unlimited:
        prompt += """
            Please summarize it in one sentence at most if your findings are vague, indefinitive, not specific, not interesting or speculative.
            Otherwise stick to one paragraph at most.
            """
    prompt += "###"
    prompt_with_chunk = prompt
    
    # Ensure stderr is flushed immediately for real-time updates
    if args.follow:
        sys.stderr.write("Data transfer started...sharing AI thoughts in stderr as we go!\n")
    else:
        sys.stderr.write("Data transfer started...sharing AI thoughts in stderr at the end after the data are through!\n")
    sys.stderr.flush()


    try:
        while True:
            # Read a chunk of data from stdin
            chunk = sys.stdin.read(chunk_size)
            if not chunk:
                # End of input (EOF) reached
                break

            # Write the chunk to stdout and ensure data is immediately written
            sys.stdout.write(chunk)
            sys.stdout.flush()

            # Query the AI and output to stderr
            if args.follow:
                prompt_with_chunk = prompt + chunk
                if prompt_with_chunk != prompt:
                    ai_response = api.generate_content(prompt_with_chunk)
                    sys.stderr.write(f'{ai_response}')
                    sys.stderr.flush()
            else:
                prompt_with_chunk += chunk

    except KeyboardInterrupt:
        sys.stderr.write("\nData transfer interrupted by user.\n")
    finally:
        # Final update and newline for clean output
        if args.follow:
            prompt_with_chunk = prompt + chunk
        if prompt_with_chunk != prompt:
            ai_response = api.generate_content(prompt_with_chunk)
            sys.stderr.write(f'{ai_response}')
            sys.stderr.flush()

# def pv_equivalent(chunk_size=4096):
#     """
#     Reads from stdin, writes to stdout, and displays data flow rate to stderr.
#     """
#     total_bytes_read = 0
#     start_time = time.time()
#     last_update_time = start_time
#     bytes_since_last_update = 0

#     # Ensure stderr is flushed immediately for real-time updates
#     sys.stderr.write("Starting data transfer...\n")
#     sys.stderr.flush()

#     try:
#         while True:
#             # Read a chunk of data from stdin
#             # For binary data, use sys.stdin.buffer.read()
#             # For text data, use sys.stdin.read(chunk_size) or sys.stdin.buffer.read()
#             # We'll use buffer for general purpose (handles binary and text bytes)
#             chunk = sys.stdin.buffer.read(chunk_size)

#             if not chunk:
#                 # End of input (EOF) reached
#                 break

#             # Write the chunk to stdout
#             # For binary data, use sys.stdout.buffer.write()
#             # For text data, use sys.stdout.write()
#             sys.stdout.buffer.write(chunk)
#             sys.stdout.buffer.flush() # Ensure data is immediately written

#             bytes_read_in_chunk = len(chunk)
#             total_bytes_read += bytes_read_in_chunk
#             bytes_since_last_update += bytes_read_in_chunk

#             current_time = time.time()
#             elapsed_total = current_time - start_time
#             elapsed_since_last_update = current_time - last_update_time

#             # Update progress every 0.5 seconds or if a significant amount of data has passed
#             if elapsed_since_last_update >= 0.5:
#                 # Calculate throughput for the last interval
#                 if elapsed_since_last_update > 0:
#                     current_rate = bytes_since_last_update / elapsed_since_last_update
#                     rate_str = format_bytes_per_second(current_rate)
#                 else:
#                     rate_str = "0 B/s"

#                 # Clear the line and print new progress to stderr
#                 # \r moves cursor to the beginning of the line
#                 # \033[K clears from cursor to end of line
#                 sys.stderr.write(f"\r{format_bytes(total_bytes_read)} [{rate_str}] (Elapsed: {format_time(elapsed_total)}){' ' * 10}\033[K")
#                 sys.stderr.flush()

#                 last_update_time = current_time
#                 bytes_since_last_update = 0

#     except KeyboardInterrupt:
#         sys.stderr.write("\nTransfer interrupted by user.\n")
#     finally:
#         # Final update and newline for clean output
#         final_time = time.time()
#         final_elapsed = final_time - start_time
#         final_rate = total_bytes_read / final_elapsed if final_elapsed > 0 else 0
#         sys.stderr.write(f"\r{format_bytes(total_bytes_read)} [{format_bytes_per_second(final_rate)}] (Elapsed: {format_time(final_elapsed)}) Complete.\n")
#         sys.stderr.flush()

# def format_bytes(bytes_count):
#     """Formats bytes into human-readable string (e.g., 1.2 MB)."""
#     if bytes_count < 1024:
#         return f"{bytes_count} B"
#     elif bytes_count < 1024**2:
#         return f"{bytes_count / 1024:.1f} KB"
#     elif bytes_count < 1024**3:
#         return f"{bytes_count / (1024**2):.1f} MB"
#     elif bytes_count < 1024**4:
#         return f"{bytes_count / (1024**3):.1f} GB"
#     else:
#         return f"{bytes_count / (1024**4):.1f} TB"

# def format_bytes_per_second(rate):
#     """Formats bytes/second into human-readable string (e.g., 1.2 MB/s)."""
#     return f"{format_bytes(rate)}/s"

# def format_time(seconds):
#     """Formats seconds into Hh Mm Ss string."""
#     seconds = int(seconds)
#     hours = seconds // 3600
#     minutes = (seconds % 3600) // 60
#     remaining_seconds = seconds % 60
#     parts = []
#     if hours > 0:
#         parts.append(f"{hours}h")
#     if minutes > 0 or hours > 0: # include minutes if hours are present or minutes are > 0
#         parts.append(f"{minutes}m")
#     parts.append(f"{remaining_seconds}s")
#     return " ".join(parts) if parts else "0s"


def parse_args():
    parser = argparse.ArgumentParser(
        __file__, description="""
            This Python script mimics pv Linux utility in term of reading from stdin, and writing to stdout. 
            But it uses stderr to print AI thoughts on data through pipe instead of monitor the progress.
            """
    )
    parser.add_argument(
        "--follow", 
        help="""
            Continuously print AI thoughts as the data are coming in from stdin. 
            Otherwise gather the data first and share the thoughts at the end.
            """,
        dest="follow",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--unlimited", 
        help="""
            AI response is not limited to sentence or paragraph
            """,
        dest="unlimited",
        action="store_true",
        default=False
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    gemini = GeminiAPI('gemini-2.0-flash-exp')
    pvai(gemini, args)
