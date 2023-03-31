"""Define the API schema."""
from pydantic import BaseModel


class ConversationRequest(BaseModel):
    """Request message to the LangChain."""

    # Message is passed directly to the LangChain
    # deployed in the plugin.
    message: str


class ConversationResponse(BaseModel):
    """Deployed LangChain response."""

    response: str
