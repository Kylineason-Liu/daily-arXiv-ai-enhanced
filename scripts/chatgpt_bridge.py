"""Use Horizon's existing, locally authorized ChatGPT provider over stdin/stdout."""
import argparse
import json
from pathlib import Path
import sys


def completed_text(stream):
    """Buffer text deltas, but release nothing unless a completed event validates them."""
    parts = []
    for event in stream:
        if event.type == 'response.output_text.delta':
            parts.append(event.delta)
        elif event.type in ('response.failed', 'response.incomplete', 'error'):
            raise RuntimeError(f'{event.type}; partial output discarded')
        elif event.type == 'response.completed':
            response = event.response
            if response.status != 'completed' or response.error is not None:
                raise RuntimeError('Invalid completion; partial output discarded')
            # Some streaming responses omit output items in the terminal payload.
            result = response.output_text or ''.join(parts)
            if not result.strip():
                raise RuntimeError('Completed response contained no text')
            return result
    raise RuntimeError('Stream ended without completion; partial output discarded')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--horizon', required=True)
    parser.add_argument('--model', required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.horizon).resolve()))
    from src.ai.chatgpt_auth import ChatGPTAuth, RESOURCE, api_error
    from openai import OpenAI, APIError

    request = json.load(sys.stdin)
    auth = ChatGPTAuth()
    status = auth.status()
    if not status['connected'] or not status['plan_usage']:
        raise RuntimeError('Horizon ChatGPT subscription authorization is required')
    token = auth.access_token(status['client_id'])
    try:
        with OpenAI(api_key=token, base_url=RESOURCE, max_retries=0, timeout=300) as client:
            with client.responses.create(model=args.model, instructions=request['system'],
                    input=[{'role': 'user', 'content': request['user']}], store=False, stream=True) as stream:
                print(completed_text(stream))
    except APIError as exc:
        raise api_error(exc.body, getattr(exc, 'status_code', None), getattr(exc, 'request_id', None)) from None


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ChatGPT subscription request failed: {exc}', file=sys.stderr)
        sys.exit(1)
