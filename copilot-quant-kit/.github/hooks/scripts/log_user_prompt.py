import sys

from hook_common import print_output, read_event, read_policy, write_audit


def main() -> None:
    """Write each prompt to the audit log (UserPromptSubmit hook).

    With the tool calls and check results already in the log, each session
    reads as: what was asked, what the agent did, and what the checks found.
    The prompt is cut to prompt_log_chars. The log stays on this machine.
    """
    event = read_event()
    policy = read_policy()
    prompt = str(event.get("prompt", ""))
    write_audit(
        policy,
        event,
        {"event": "prompt", "prompt": prompt[: policy["prompt_log_chars"]]},
    )
    print_output("UserPromptSubmit", {})


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"log_user_prompt error: {error}", file=sys.stderr)
        print("{}")
