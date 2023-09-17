#!/usr/bin/env python
import argparse
from enum import Enum
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time

import tiktoken
import openai

MAX_SESSION_LENGTH = 120
MAX_SESSION_TOKENS = 10000


class OutputFormat(Enum):
    JSON = 'json'
    TEXT = 'text'
    MARKDOWN = 'markdown'


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)


# info or warn or debug
def configure_logging():
    debug_level = os.getenv("LOGGING_LEVEL", "INFO")
    root = logging.getLogger()
    root.setLevel(debug_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(debug_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    logging.getLogger().setLevel(debug_level)
    logger = logging.getLogger()
    return logger


def parse_cli_arguments():
    parser = argparse.ArgumentParser(
        description='Demonstrate the kubernetes_gpt project')
    parser.add_argument('--openai-key',
                        default=OPENAI_API_KEY,
                        help='As the name suggests.')
    parser.add_argument('--output',
                        choices=[OutputFormat.JSON.value,
                                 OutputFormat.TEXT.value,
                                 OutputFormat.MARKDOWN.value],
                        default=OutputFormat.JSON.value,
                        help='As the name suggests.')
    args = parser.parse_args()
    return args


def format_chat(chat_messages, format_type="plain_text"):
    result = ''
    if format_type == OutputFormat.JSON.value:
        result = json.dumps(chat_messages, indent=2)
    elif format_type == OutputFormat.TEXT.value:
        for message in chat_messages:
            role = message.get("role")
            content = message.get("content")

            if role == "system":
                content = ' '.join(content.split())
            elif role == "assistant":
                # Remove code block formatting for assistant messages
                content = content.replace("```", "")
            result += f"{role.capitalize()}: {content}\n"
    elif format_type == OutputFormat.MARKDOWN.value:
        for message in chat_messages:
            role = message.get("role")
            content = message.get("content")

            if role == "system":
                # Wrap system messages in code block for Markdown
                content = f"system:\n\n```\n{content}\n```"
            elif role == "assistant":
                # Wrap assistant messages in code block for Markdown
                content = f"```\n{content}\n```"
            result += content + "\n"
    else:
        raise Exception(f"Invalid format_type: {format_type}")

    return result


#
#
#
def troubleshoot_cluster():

    gpt_model = "gpt-3.5-turbo"

    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    encoding = tiktoken.get_encoding("cl100k_base")
    encoding = tiktoken.encoding_for_model(gpt_model)
    conversation_tokens = 0

    # Read basic portions of prompt
    with open("prompts/troubleshoot-output-too-long.txt", "r") as file:
        prompt_output_too_long = file.read()
    with open("prompts/troubleshoot-assess.txt", "r") as file:
        base_prompt = file.read()
    with open("prompts/troubleshoot-stress-no-placeholder.txt", "r") as file:
        stress_no_placeholder = file.read()
    with open("prompts/troubleshoot-stress-single-command.txt", "r") as file:
        stress_single_command = file.read()
    with open("prompts/troubleshoot-session-too-long.txt", "r") as file:
        prompt_session_too_long = file.read()

    chat_messages = [
        {"role": "system",
         "content": base_prompt}
    ]

    try:
        kube_env = os.environ
        subprocess.check_call(["kubectl",
                               "get",
                               "nodes"])
    except subprocess.CalledProcessError:
        logging.getLogger().error("kubectl command line is not logged in.")
        raise Exception("Unable to validate connection to Kubernetes server.")

    # Create a temporary working directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        logger.info(f"Working in temporary directory: {temp_dir}")

        new_command = ""
        consecutive_nudges = 0
        consecutive_errors = 0
        wrap_it_up = False
        session_over = False
        while not session_over:
            conversation = format_chat(chat_messages, OutputFormat.TEXT.value)
            logger.debug(f"Current conversation:\n\n{conversation}")

            if wrap_it_up:
                session_over = True
            else:
                conversation_tokens = len(encoding.encode(conversation))
                if conversation_tokens > MAX_SESSION_TOKENS or \
                        len(chat_messages) > MAX_SESSION_LENGTH:
                    chat_messages.append({
                        "role": "user",
                        "content": prompt_session_too_long})
                    logger.info((
                        "INFO: Context became too long: "
                        f"{conversation_tokens} tokens, "
                        f"{len(chat_messages)} interactions"))
                    wrap_it_up = True

            # The model with the larger 16k token context
            # is 2x the price per token than the regular
            # 4k token.
            if conversation_tokens > 4000 and \
                    gpt_model == "gpt-3.5-turbo":
                gpt_model = "gpt-3.5-turbo-16k"
                logger.info((f"Switching to {gpt_model} model "
                             "to accommodate longer conversation."))

            # Generate text using the OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model=gpt_model,
                    messages=chat_messages
                )
            except openai.InvalidRequestError as e:
                logger.error(e)
                break

            gpt_response_message = response['choices'][0]['message']
            gpt_response_content = gpt_response_message['content']
            gpt_response_role = gpt_response_message['role']
            # gpt_response_role = "assistant"
            # gpt_response_content = (
            #     "OK, let's start with the "
            #     "first item on the checklist: Nodes.\n\nTo check the "
            #     "overall status of the nodes in the cluster, please "
            #     "run the following command:\n\n"
            #     "```\nkubectl get nodes\n"
            #     "###")

            chat_messages.append({
                "role": gpt_response_role,
                "content": gpt_response_content
                })

            if session_over or \
                    "++++" in gpt_response_content or \
                    "good luck" in gpt_response_content.lower():
                session_over = True
                logger.info("ChatGPT concluded the session")
                continue

            if consecutive_nudges > 3:
                chat_messages.append({
                    "role": "user",
                    "content": "Let's move on with the assessment."
                    })
                consecutive_nudges = 0
                continue

            match = re.search(r'kubectl\s+[^\n]+', gpt_response_content)
            if match:
                new_command = match.group(0)
            else:
                chat_messages.append({
                    "role": "user",
                    "content": stress_single_command})
                consecutive_nudges += 1
                continue

            parameter = re.findall(r'<[a-zA-Z0-9_-]+>', new_command)
            if len(parameter) > 0:
                chat_messages.append({
                    "role": "user",
                    "content": stress_no_placeholder})
                consecutive_nudges += 1
                continue

            logger.debug(f"About to run command: {new_command}")
            now = time.time()
            try:
                command_output_b = subprocess.check_output(
                        ["/bin/sh", "-c", new_command],
                        env=kube_env,
                        stderr=subprocess.STDOUT,
                        timeout=30)
                command_output = command_output_b.decode('utf-8')
                exec_time = time.time() - now
            except subprocess.CalledProcessError as e:
                command_output = e.output.decode('utf-8')
                logger.error((f"The command failed: [{e.returncode}]\n"
                              f"{command_output}"))
                chat_messages.append({
                    "role": "user",
                    "content": command_output})
                consecutive_errors += 1
                if consecutive_errors > 6:
                    logger.info(("Troubleshooting is not converging. "
                                 "Ending the session"))
                    break
                elif consecutive_errors > 3:
                    move_on_msg = ("There are too many errors attempting to "
                                   "assess this items in the checklist. "
                                   "Please move on to the next item")
                    chat_messages.append({
                        "role": "user",
                        "content": move_on_msg})
                continue

            if exec_time >= 30:
                timeout_msg = "The command timed out after 30 seconds."
                chat_messages.append({
                    "role": "user",
                    "content": timeout_msg})

            logger.debug(f"Output:\n{command_output}")

            command_output_len = len(encoding.encode(command_output))
            if command_output_len == 0:
                command_returned_empty = "The command returned no output."
                chat_messages.append({
                    "role": "user",
                    "content": command_returned_empty})
            elif command_output_len <= 500:
                chat_messages.append({"role": "user",
                                      "content": command_output})
            else:
                chat_messages.append({"role": "user",
                                      "content": prompt_output_too_long})
                consecutive_nudges += 1
                continue

            consecutive_nudges = 0

    conversation_tokens = len(encoding.encode(
        format_chat(chat_messages,
                    OutputFormat.TEXT.value)))
    logger.info((f"Troubleshooting session ended with {len(chat_messages)} "
                 f"exchanges and {conversation_tokens} tokens"))
    return chat_messages


#
#
#
if __name__ == '__main__':
    logger = configure_logging()

    args = parse_cli_arguments()
    openai_key = args.openai_key
    chat_messages = troubleshoot_cluster()

    output_format = args.output
    result = format_chat(chat_messages, output_format)
    print(result)
