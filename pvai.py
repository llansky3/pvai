import sys
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

def parse_args():
    parser = argparse.ArgumentParser(
        __file__, description="""
            This Python script mimics pv Linux utility in terms of reading from stdin, and writing to stdout. 
            But it uses stderr to print AI thoughts on data going through pipe instead of monitoring the progress.
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
