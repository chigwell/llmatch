[![PyPI version](https://badge.fury.io/py/llmatch.svg)](https://badge.fury.io/py/llmatch)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Downloads](https://static.pepy.tech/badge/llmatch)](https://pepy.tech/project/llmatch)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# LLM Match

LLM Match (`llmatch`) is a Python utility function designed to reliably interact with Language Models integrated via LangChain (`langchain-core`, `langchain-llm7`). It ensures the LLM's responses conform to a specified regular expression pattern, implementing automatic retries with exponential backoff for increased robustness against transient issues or non-conforming responses.

It's particularly useful when you need structured data or specific formatting from an LLM and want to enforce that structure programmatically.

## Installation

To install `llmatch`, use pip. This will also install necessary dependencies like `langchain-core` and `langchain-llm7`.

```bash
pip install llmatch langchain-llm7 langchain-core
````

*(Note: You need to have a compatible LangChain LLM environment set up for `llmatch` to make actual LLM calls. The default `ChatLLM7()` might be a placeholder or require specific configuration.)*

## Usage

Using `llmatch` involves providing a query, optional context, and a regex pattern you expect the LLM's response to match. It will handle the LLM invocation and retries until a matching response is found or the maximum retries are exceeded.

Here's a more meaningful example where we ask the LLM to summarize a piece of code and return the summary enclosed in specific XML-like tags:

```python
# Import the function and potentially your configured LLM
from llmatch import llmatch
# from langchain_your_provider import YourChatLLM # Example if not using default

# Example context: A Python code snippet
code_context = """
import logging
import sys

def setup_logger(log_file_path="app.log"):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO) # Set root logger level

    # Prevent duplicate handlers if logger is already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Console level

    try:
        # File Handler - Append Mode
        file_handler = logging.FileHandler(log_file_path, mode='a')
        file_handler.setLevel(logging.ERROR) # Log only errors and critical to file

        # Create formatter and add to handlers
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        logger.info(f"Logging initialized. INFO to console, ERROR to {log_file_path}")

    except Exception as log_error:
        print(f"WARNING: Error setting up log file: {log_error}")
        # Fallback to console-only logging
        logger.addHandler(console_handler)
        logger.info("Logging initialized to console only.")

    return logger

# Example usage of the logger setup
# if __name__ == "__main__":
#     my_logger = setup_logger()
#     my_logger.info("This is an info message.")
#     my_logger.error("This is an error message.")
"""

# Define the query for the LLM
query = "Summarize the purpose of the following Python code in one sentence."

# Define the regex pattern to extract the summary from within <summary> tags
# We expect the LLM to respond like: "Some text... <summary>The summary text.</summary> ...more text"
pattern = r"<summary>(.*?)</summary>"

# Initialize your LangChain LLM (replace ChatLLM7() if necessary)
# llm_instance = YourChatLLM(temperature=0.7)
# For this example, we'll use the default which might be a dummy/placeholder
# from langchain_llm7 import ChatLLM7
# llm_instance = ChatLLM7()

# Call llmatch
# Note: We might need to explicitly pass the llm_instance if not using the default
result = llmatch(
    # llm=llm_instance, # Pass your configured LLM here
    query=query,
    context=code_context,
    pattern=pattern, # Specify the desired pattern for extraction
    max_retries=3,    # Limit retries for the example
    verbose=False     # Set to True for detailed logs
)

# Process the result
print("\n--- LLMatch Result ---")
if result["success"]:
    print("Successfully extracted summary:")
    # findall returns a list, get the first match
    extracted_summary = result["extracted_data"][0]
    print(f"> {extracted_summary}")
    # print("\nFull LLM Response:")
    # print(result["final_content"])
else:
    print(f"Failed to get a matching response after {result['retries_attempted']} retries.")
    print(f"Error: {result['error_message']}")
    # print("\nLast LLM Response Attempt:")
    # print(result["final_content"])

```

In this example, `llmatch` repeatedly prompts the LLM with the query and context, checking each response against the `<summary>(.*?)</summary>` pattern. It only returns successfully once the LLM provides a response containing that structure, extracting the text within the tags.

## Features

  - **Reliable LLM Interaction**: Automatically retries LLM calls on failure or non-matching responses.
  - **Exponential Backoff**: Waits progressively longer between retries to handle transient load or rate limits.
  - **Response Validation**: Uses regular expressions (`pattern`) to ensure the LLM response conforms to the desired structure.
  - **Data Extraction**: Extracts specific parts of the LLM response using regex capture groups.
  - **Configurable**: Allows customization of the query, context, regex pattern, prompt template, retry attempts, and delay parameters.
  - **LangChain Integration**: Designed to work with LangChain LLM objects (tested with `langchain-llm7` and `langchain-core`).
  - **Debugging**: Includes a `verbose` mode for detailed logging of the process.

## Contributing

Contributions, issues, and feature requests are welcome\! Feel free to check the [issues page](https://github.com/chigwell/llmatch/issues).

## License

`llmatch` is licensed under the [Apache License 2.0](https://opensource.org/licenses/Apache-2.0).
