import sys

from hook_common import print_output, read_event, read_policy, write_audit


def main() -> None:
    """Give every subagent the core project rules (SubagentStart hook).

    Subagents start with a short prompt and can miss the instruction files.
    The rules text is in hook_policy.json (subagent_rules), so there is one
    place to change it.
    """
    event = read_event()
    policy = read_policy()
    agent = event.get("agentName", event.get("agent_type", ""))
    write_audit(policy, event, {"event": "subagent_start", "agent": agent})
    print_output("SubagentStart", {"additionalContext": policy["subagent_rules"]})


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"add_subagent_rules error: {error}", file=sys.stderr)
        print("{}")
