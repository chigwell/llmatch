import re
import time
from typing import Any, Dict, List, Optional, Pattern, Type

from langchain_llm7 import ChatLLM7
from langchain_core.messages import HumanMessage, BaseMessage



# --- The Reusable Function Template ---
def llmatch(
    llm: Optional[ChatLLM7] = ChatLLM7(),
    query: str = "Extract relevant data.",
    pattern: Optional[str | Pattern] = "```(.*?)```", # Default pattern to match ```-like tags
    context: Optional[str] = None, # Optional additional text/context for the prompt
    prompt_template: str = "{query}\n\n{context}\\nWrite the answer in the next format: {format}",
    max_retries: int = 15,
    initial_delay: float = 1.0, # Initial delay in seconds before first retry
    backoff_factor: float = 1.5, # Factor to increase delay (e.g., 1.5 = 50% increase each retry)
    verbose: bool = False,
    **kwargs: Any # Catch-all for future/other custom parameters (not passed to LLM by default)
) -> Dict[str, Any]:
    """
    Invokes an LLM, retrying until a response matches the pattern or max_retries is reached.

    Args:
        llm: An already initialized instance of the LLM. If None,
                      a new one is created using llm_class and llm_params.
        query: The main query or instruction for the LLM.
        pattern: A regex string or compiled re.Pattern object to search for in the
                 LLM's response content. If None, the function returns the first
                 successful response without pattern matching.
        context: Optional additional text to provide context to the LLM.
        prompt_template: A format string to combine query and context.
                         Should contain '{query}' and '{context}' placeholders.
                         Context placeholder will be empty if context is None.
        max_retries: Maximum number of attempts to make.
        initial_delay: Seconds to wait before the first retry.
        backoff_factor: Multiplier for the delay between retries (exponential backoff).
        verbose: If True, prints detailed logs of the process.
        pass_through_args: Dictionary of keyword arguments to pass directly to the
                           `llm_instance.invoke()` method.
        **kwargs: Catches any other keyword arguments passed to the function for future use
                  (they are not used in the core logic currently).

    Returns:
        A dictionary containing:
        - 'success' (bool): True if a valid response (matching pattern if provided) was found.
        - 'extracted_data' (Optional[List[str]]): List of strings matching the pattern (groups),
                                                  or None if no pattern was provided or matched.
        - 'final_content' (Optional[str]): The content of the last successful or final failed LLM response.
        - 'retries_attempted' (int): Number of retries made (0 means success on first try).
        - 'error_message' (Optional[str]): Description of the error if success is False.
        - 'raw_response' (Any): The raw response object from the last LLM call (could be None if instantiation failed).
    """

    if pattern and isinstance(pattern, str):
        try:
            compiled_pattern = re.compile(pattern, re.DOTALL)
            if verbose:
                print(f"Compiled regex pattern: {pattern}")
        except re.error as e:
             if verbose:
                print(f"Error: Invalid regex pattern provided: {pattern}. Error: {e}")
             return {
                "success": False, "extracted_data": None, "final_content": None,
                "retries_attempted": 0, "error_message": f"Invalid regex pattern: {e}",
                "raw_response": None,
             }
    elif isinstance(pattern, re.Pattern):
         compiled_pattern = pattern
         if verbose:
             print(f"Using provided compiled regex pattern: {compiled_pattern.pattern}")
    else:
        compiled_pattern = None
        if verbose:
            print("No pattern provided. Will return first valid response.")

    # --- Prepare Prompt ---
    context_str = context if context is not None else ""
    try:
        full_prompt = prompt_template.format(query=query, context=context_str, format=str(pattern))
    except KeyError:
         if verbose:
             print("Warning: prompt_template is missing '{query}' or '{context}' or '{format}'. Using basic query.")
         full_prompt = query + ("\n\n" + context_str if context_str else "")

    # --- Prepare Messages (adjust structure as needed for your LLM) ---
    messages: List[BaseMessage] = [HumanMessage(content=full_prompt)]
    # You might add SystemMessage, etc. here if needed:
    # messages.insert(0, SystemMessage(content="You are an expert data extractor."))

    # --- Retry Loop ---
    retry_count = 0
    current_delay = initial_delay
    last_error = None
    final_content = None
    raw_response = None

    while retry_count <= max_retries:
        attempt = retry_count + 1
        if verbose:
            print(f"\n--- LLM Invocation: Attempt {attempt}/{max_retries + 1} ---")
            # Avoid logging potentially sensitive full messages unless necessary
            # print(f"Messages: {messages}")

        try:

            response = llm.invoke(messages)
            raw_response = response # Store last raw response

            # 1. Validate response structure
            if not response or not hasattr(response, 'content'):
                last_error = "Invalid response object structure received from LLM."
                if verbose:
                    print(f"Error: {last_error} Response: {response}")
                # Decide if this specific error warrants a retry or immediate failure
                # Let's retry for now.
                retry_count += 1
                if retry_count <= max_retries: time.sleep(current_delay); current_delay *= backoff_factor
                continue

            content = response.content
            final_content = content # Store last received content

            # 2. Validate content type
            if not isinstance(content, str):
                last_error = f"LLM response content is not a string (type: {type(content)})."
                if verbose:
                    print(f"Error: {last_error} Content: {content}")
                # Let's retry for now.
                retry_count += 1
                if retry_count <= max_retries: time.sleep(current_delay); current_delay *= backoff_factor
                continue

            if verbose:
                print(f"Raw Response Content: {content}")

            # 3. Match Pattern (if provided)
            if compiled_pattern:
                extracted_data = compiled_pattern.findall(content)
                if extracted_data:
                    if verbose:
                        print(f"Success: Pattern '{compiled_pattern.pattern}' found.")
                        print(f"Extracted Data: {extracted_data}")
                    return {
                        "success": True,
                        "extracted_data": extracted_data,
                        "final_content": content,
                        "retries_attempted": retry_count,
                        "error_message": None,
                        "raw_response": raw_response,
                    }
                else:
                    last_error = f"Pattern '{compiled_pattern.pattern}' not found in response."
                    if verbose:
                        print(f"Info: {last_error}")
                    # Continue to retry
            else:
                # No pattern provided, first valid string response is success
                if verbose:
                    print("Success: Valid string response received (no pattern matching required).")
                return {
                    "success": True,
                    "extracted_data": None, # No pattern to extract
                    "final_content": content,
                    "retries_attempted": retry_count,
                    "error_message": None,
                    "raw_response": raw_response,
                }

        except Exception as e:
            last_error = f"Exception during LLM invocation: {e}"
            if verbose:
                print(f"Error: {last_error}")
            # Continue to retry after exception

        # --- Prepare for next retry ---
        retry_count += 1
        if retry_count <= max_retries:
            if verbose:
                print(f"Retrying in {current_delay:.2f} seconds...")
            time.sleep(current_delay)
            current_delay *= backoff_factor # Increase delay for next time

    # --- End of Retries ---
    if verbose:
        print("\n--- Max retries reached or loop exited ---")

    return {
        "success": False,
        "extracted_data": None,
        "final_content": final_content, # Content from the very last attempt
        "retries_attempted": retry_count -1, # How many retries were actually done
        "error_message": last_error or "Max retries reached without success.",
        "raw_response": raw_response, # Raw response from the very last attempt
    }

