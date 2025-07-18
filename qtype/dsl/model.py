from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    """Base model with extra fields forbidden."""

    model_config = ConfigDict(extra="forbid")


class VariableType(str, Enum):
    """Represents the type of data a user or system input can accept within the DSL.
    Used for schema validation and UI rendering of input fields."""

    text = "text"
    number = "number"
    file = "file"
    image = "image"
    date = "date"
    time = "time"
    datetime = "datetime"
    video = "video"
    audio = "audio"


class DisplayType(str, Enum):
    """UI rendering hint for how an input should appear in the frontend (e.g., text box, dropdown, file upload)."""

    text = "text"
    textarea = "textarea"
    dropdown = "dropdown"
    file_upload = "file_upload"
    checkbox = "checkbox"
    slider = "slider"
    radio = "radio"
    group = "group"
    section = "section"


class DisplayMetadata(StrictBaseModel):
    """Additional UI hints used to customize how input fields are displayed in the generated application UI."""

    placeholder: Optional[str] = Field(
        default=None,
        description="Placeholder text shown inside the input field.",
    )
    tooltip: Optional[str] = Field(
        default=None, description="Tooltip shown on hover."
    )
    default_value: Optional[Any] = Field(
        default=None,
        description="Default value if the user doesn't supply one.",
    )
    min_value: Optional[Union[int, float]] = Field(
        default=None, description="Minimum value for numeric inputs."
    )
    max_value: Optional[Union[int, float]] = Field(
        default=None, description="Maximum value for numeric inputs."
    )
    step: Optional[Union[int, float]] = Field(
        default=None, description="Step size for numeric inputs."
    )
    allowed_types: Optional[List[str]] = Field(
        default=None, description="Allowed file types for file upload."
    )
    options: Optional[List[str]] = Field(
        default=None,
        description="Options for dropdowns, radios, or checkboxes.",
    )
    group: Optional[str] = Field(
        default=None, description="Grouping section this input belongs to."
    )
    section: Optional[str] = Field(
        default=None,
        description="Section name used to visually separate inputs.",
    )
    icon: Optional[str] = Field(
        default=None, description="Icon shown alongside input (optional)."
    )
    css_class: Optional[str] = Field(
        default=None, description="Optional CSS class for advanced styling."
    )


class Variable(StrictBaseModel):
    """Schema for a variable that can serve as input, output, or parameter within the DSL."""

    id: str = Field(
        ...,
        description="Unique ID of the variable. Referenced in prompts or steps.",
    )
    type: VariableType = Field(
        ..., description="Type of data expected or produced."
    )
    display_name: Optional[str] = Field(
        default=None, description="Label shown in the UI."
    )
    display_type: Optional[DisplayType] = Field(
        default=None, description="Hint for how to render this variable."
    )
    display_metadata: Optional[DisplayMetadata] = Field(
        default=None, description="Additional UI hints."
    )


class Prompt(StrictBaseModel):
    """References a prompt template, either inline or from file, along with expected input and output variable bindings."""

    id: str = Field(..., description="Unique ID for the prompt.")
    path: Optional[str] = Field(
        default=None, description="File path to the prompt template."
    )
    template: Optional[str] = Field(
        default=None, description="Inline template string for the prompt."
    )
    inputs: List[str] = Field(
        ..., description="List of input variable IDs this prompt expects."
    )
    outputs: Optional[List[str]] = Field(
        default=None,
        description="Optional list of output variable IDs this prompt generates.",
    )


class Model(StrictBaseModel):
    """Describes a generative model configuration, including provider and model ID."""

    id: str = Field(..., description="Unique ID for the model.")
    provider: str = Field(
        ..., description="Name of the provider, e.g., openai or anthropic."
    )
    model_id: Optional[str] = Field(
        default=None,
        description="The specific model name or ID for the provider. If None, id is used",
    )
    inference_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional inference parameters like temperature or max_tokens.",
    )
    dimensions: Optional[int] = Field(
        default=None,
        description="Dimensionality of the embedding vectors produced by this model if an embedding model.",
    )

class VectorDBRetriever(StrictBaseModel):
    """Retriever that fetches top-K documents using a vector database and embedding-based similarity search."""

    type: Literal["vector_retrieve"] = "vector_retrieve"
    id: str = Field(..., description="Unique ID of the retriever.")
    index: str = Field(..., description="ID of the index this retriever uses.")
    embedding_model: str = Field(
        ...,
        description="ID of the embedding model used to vectorize the query.",
    )
    top_k: int = Field(5, description="Number of top documents to retrieve.")
    args: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Arbitrary arguments as JSON/YAML for custom retriever configuration.",
    )
    inputs: Optional[List[str]] = Field(
        default=None,
        description="Input variable IDs required by this retriever.",
    )
    outputs: Optional[List[str]] = Field(
        default=None,
        description="Optional list of output variable IDs this prompt generates.",
    )


class MemoryType(str, Enum):
    """Enum to differentiate supported memory types, such as vector memory for embedding-based recall."""

    vector = "vector"


class Memory(StrictBaseModel):
    """Session or persistent memory used to store relevant conversation or state data across steps or turns."""

    id: str = Field(..., description="Unique ID of the memory block.")
    type: MemoryType = Field(
        ..., description="The type of memory to store context."
    )
    embedding_model: str = Field(
        ..., description="Embedding model ID used for storage."
    )
    persist: bool = Field(
        default=False, description="Whether memory persists across sessions."
    )
    ttl_minutes: Optional[int] = Field(
        default=None, description="Optional TTL for temporary memory."
    )
    use_for_context: bool = Field(
        default=True,
        description="Whether this memory should be injected as context.",
    )

class Tool(StrictBaseModel):
    """Callable function or external operation available to the model. Input/output shapes are described via JSON Schema."""

    type: Literal["tool"]
    id: str = Field(..., description="Unique ID of the tool.")
    name: str = Field(..., description="Name of the tool function.")
    description: str = Field(
        ..., description="Description of what the tool does."
    )
    inputs: List[str] = Field(
        ..., description="List of input variable IDs this prompt expects."
    )
    outputs: List[str] = Field(
        ...,
        description="Optional list of output variable IDs this prompt generates.",
    )


class ToolProvider(StrictBaseModel):
    """Logical grouping of tools, often backed by an API or OpenAPI spec, and optionally authenticated.

    This should show the Pydantic fields."""

    id: str = Field(..., description="Unique ID of the tool provider.")
    name: str = Field(..., description="Name of the tool provider.")
    tools: List[Tool] = Field(
        ..., description="List of tools exposed by this provider."
    )
    openapi_spec: Optional[str] = Field(
        default=None,
        description="Optional path or URL to an OpenAPI spec to auto-generate tools.",
    )
    include_tags: Optional[List[str]] = Field(
        default=None,
        description="Limit tool generation to specific OpenAPI tags.",
    )
    exclude_paths: Optional[List[str]] = Field(
        default=None, description="Exclude specific endpoints by path."
    )
    auth: Optional[str] = Field(
        default=None,
        description="AuthorizationProvider ID used to authenticate tool access.",
    )


class AuthorizationProvider(StrictBaseModel):
    """Defines how tools or providers authenticate with APIs, such as OAuth2 or API keys."""

    id: str = Field(
        ..., description="Unique ID of the authorization configuration."
    )
    type: str = Field(
        ..., description="Authorization method, e.g., 'oauth2' or 'api_key'."
    )
    host: Optional[str] = Field(
        default=None, description="Base URL or domain of the provider."
    )
    client_id: Optional[str] = Field(
        default=None, description="OAuth2 client ID."
    )
    client_secret: Optional[str] = Field(
        default=None, description="OAuth2 client secret."
    )
    token_url: Optional[str] = Field(
        default=None, description="Token endpoint URL."
    )
    scopes: Optional[List[str]] = Field(
        default=None, description="OAuth2 scopes required."
    )
    api_key: Optional[str] = Field(
        default=None, description="API key if using token-based auth."
    )


class TelemetrySink(StrictBaseModel):
    """Defines an observability endpoint for collecting telemetry data from the QType runtime."""

    id: str = Field(
        ..., description="Unique ID of the telemetry sink configuration."
    )
    endpoint: str = Field(
        ..., description="URL endpoint where telemetry data will be sent."
    )
    auth: Optional[str] = Field(
        default=None,
        description="AuthorizationProvider ID used to authenticate telemetry data transmission.",
    )


class FeedbackType(str, Enum):
    """Enum of supported feedback mechanisms such as thumbs, stars, or text responses."""

    THUMBS = "thumbs"
    STAR = "star"
    TEXT = "text"
    RATING = "rating"
    CHOICE = "choice"
    BOOLEAN = "boolean"


class Feedback(StrictBaseModel):
    """Schema to define how user feedback is collected, structured, and optionally used to guide future prompts."""

    id: str = Field(..., description="Unique ID of the feedback config.")
    type: FeedbackType = Field(..., description="Feedback mechanism type.")
    question: Optional[str] = Field(
        default=None,
        description="Question to show user for qualitative feedback.",
    )
    prompt: Optional[str] = Field(
        default=None,
        description="ID of prompt used to generate a follow-up based on feedback.",
    )


class Condition(StrictBaseModel):
    """Conditional logic gate within a flow. Supports branching logic for execution based on variable values."""

    if_var: str = Field(..., description="ID of the variable to evaluate.")
    equals: Optional[Union[str, int, float, bool]] = Field(
        default=None, description="Match condition for equality check."
    )
    exists: Optional[bool] = Field(
        default=None, description="Condition to check existence of a variable."
    )
    then: List[str] = Field(
        ..., description="List of step IDs to run if condition matches."
    )
    else_: Optional[List[str]] = Field(
        default=None,
        alias="else",
        description="Optional list of step IDs to run if condition fails.",
    )


class Actionable(StrictBaseModel):
    """Base class for components that can be executed with inputs and outputs."""

    id: str = Field(..., description="Unique ID of this component.")
    inputs: Optional[List[str]] = Field(
        default=None,
        description="Input variable IDs required by this component.",
    )
    outputs: Optional[List[str]] = Field(
        default=None, description="Variable IDs where output is stored."
    )


class FlowMode(str, Enum):
    """Execution context for the flow. `chat` maintains history, while `complete` operates statelessly."""

    chat = "chat"
    complete = "complete"


class Flow(Actionable):
    """Composable structure that defines the interaction logic for a generative AI application.
    Supports branching, memory, and sequencing of steps."""

    mode: FlowMode = Field(..., description="Interaction mode for the flow.")
    steps: List[Union[Step, str]] = Field(
        default_factory=list, description="List of steps or nested step IDs."
    )
    conditions: Optional[List[Condition]] = Field(
        default=None, description="Optional conditional logic within the flow."
    )
    memory: Optional[List[str]] = Field(
        default=None,
        description="List of memory IDs to include (chat mode only).",
    )


class Agent(Actionable):
    type: Literal["agent"] = "agent"
    model: str = Field(
        ..., description="The id of the model for this agent to use."
    )
    prompt: str = Field(
        ..., description="The id of the prompt for this agent to use"
    )
    tools: Optional[List[str]] = Field(
        default=None, description="Tools that this agent has access to"
    )


Step = Annotated[Union[Agent, Tool, VectorDBRetriever], Field(discriminator="type")]


class QTypeSpec(StrictBaseModel):
    """The root configuration object for a QType AI application. Includes flows, models, tools, and more.
    This object is expected to be serialized into YAML and consumed by the QType runtime."""

    version: str = Field(
        ..., description="Version of the QType specification schema used."
    )
    models: Optional[List[Model]] = Field(
        default=None,
        description="List of generative models available for use, including their providers and inference parameters.",
    )
    variables: Optional[List[Variable]] = Field(
        default=None,
        description="Variables or parameters exposed by the application.",
    )
    prompts: Optional[List[Prompt]] = Field(
        default=None,
        description="Prompt templates used in generation steps or tools, referencing input and output variables.",
    )
    tool_providers: Optional[List[ToolProvider]] = Field(
        default=None,
        description="Tool providers with optional OpenAPI specs, exposing callable tools for the model.",
    )
    flows: Optional[List[Flow]] = Field(
        default=None,
        description="Entry points to application logic. Each flow defines an executable composition of steps.",
    )
    agents: Optional[List[Agent]] = Field(
        default=None,
        description="AI agents with specific models, prompts, and tools for autonomous task execution.",
    )
    feedback: Optional[List[Feedback]] = Field(
        default=None,
        description="Feedback configurations for collecting structured or unstructured user reactions to outputs.",
    )
    memory: Optional[List[Memory]] = Field(
        default=None,
        description="Session-level memory contexts, only used in chat-mode flows to persist state across turns.",
    )
    auth: Optional[List[AuthorizationProvider]] = Field(
        default=None,
        description="Authorization providers and credentials used to access external APIs or cloud services.",
    )
    telemetry: Optional[List[TelemetrySink]] = Field(
        default=None,
        description="Telemetry sinks for collecting observability data from the QType runtime.",
    )
