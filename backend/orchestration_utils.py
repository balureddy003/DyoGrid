# stop_when_done.py
from autogen_agentchat.teams import GroupChatManager
from autogen_agentchat.messages import StopMessage, ToolAgentResponse

class StopWhenDone(GroupChatManager):
    """End the loop as soon as a tool returns, an explicit StopMessage arrives,
    or the manager/assistant says a 'done' phrase."""
    DONE_MARKERS = {
        "task is finished",
        "we have completed",
        "all set",
        "done",
        "✅",
    }

    def is_final(self, message) -> bool:
        if isinstance(message, (StopMessage, ToolAgentResponse)):
            return True
        if message.content:
            lower = message.content.lower()
            if any(tok in lower for tok in self.DONE_MARKERS):
                return True
        return False