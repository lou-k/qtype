"""
Semantic Intermediate Representation (IR) models.

This module contains the semantic IR models that represent a resolved QType specification
where all ID references have been replaced with actual object references.
"""
from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, Field

# Import enums and simple classes from DSL that don't need IR-specific modifications
from qtype.dsl.models import (
    AuthorizationProvider,
    BaseRetriever,
    FeedbackType,
    FlowMode,
    MemoryType,
    Input,
    Tool,
    Output
)


class Prompt(BaseModel):
    """Points to a prompt template used for generation."""

    id: str = Field(..., description="Unique ID for the prompt.")
    path: Optional[str] = Field(None, description="File path to the prompt template.")
    template: Optional[str] = Field(
        None, description="Inline template string for the prompt."
    )
    input_vars: List[Input] = Field(
        ..., description="List of input objects this prompt expects."
    )
    output_vars: Optional[List[Output]] = Field(
        None, description="Optional list of output objects this prompt generates."
    )


class Model(BaseModel):
    """Represents a generative model configuration."""

    id: str = Field(..., description="Unique ID for the model.")
    provider: str = Field(
        ..., description="Name of the provider, e.g., openai or anthropic."
    )
    model_id: Optional[str] = Field(
        None,
        description="The specific model name or ID for the provider. If None, id is used",
    )
    inference_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional inference parameters like temperature or max_tokens.",
    )


class EmbeddingModel(Model):
    """Describes a model used for embedding text for vector search or memory."""
    
    dimensions: int = Field(
        ..., description="Dimensionality of the embedding vectors produced by this model."
    )


class VectorDBRetriever(BaseRetriever):
    """Retriever that queries a vector database using an embedding-based search."""

    embedding_model: EmbeddingModel = Field(
        ..., description="Embedding model object used to vectorize the query."
    )
    top_k: int = Field(5, description="Number of top documents to retrieve.")


class SearchRetriever(BaseRetriever):
    """Retriever that queries a keyword or hybrid search engine."""

    top_k: int = Field(5, description="Number of top documents to retrieve.")
    query_prompt: Optional[Prompt] = Field(
        None, description="Prompt object used to generate the search query."
    )


class Memory(BaseModel):
    """Persistent or session-level memory context for a user or flow."""

    id: str = Field(..., description="Unique ID of the memory block.")
    type: MemoryType = Field(..., description="The type of memory to store context.")
    embedding_model: EmbeddingModel = Field(
        ..., description="Embedding model object used for storage."
    )
    persist: bool = Field(
        default=False, description="Whether memory persists across sessions."
    )
    ttl_minutes: Optional[int] = Field(
        None, description="Optional TTL for temporary memory."
    )
    use_for_context: bool = Field(
        default=True, description="Whether this memory should be injected as context."
    )

class ToolProvider(BaseModel):
    """Wraps and authenticates access to a set of tools (often from a single API or OpenAPI spec)."""

    id: str = Field(..., description="Unique ID of the tool provider.")
    name: str = Field(..., description="Name of the tool provider.")
    tools: List[Tool] = Field(
        ..., description="List of tools exposed by this provider."
    )
    openapi_spec: Optional[str] = Field(
        None,
        description="Optional path or URL to an OpenAPI spec to auto-generate tools.",
    )
    include_tags: Optional[List[str]] = Field(
        None, description="Limit tool generation to specific OpenAPI tags."
    )
    exclude_paths: Optional[List[str]] = Field(
        None, description="Exclude specific endpoints by path."
    )
    auth: Optional['AuthorizationProvider'] = Field(
        None, description="AuthorizationProvider object used to authenticate tool access."
    )



class Feedback(BaseModel):
    """Describes how and where to collect feedback on generated responses."""

    id: str = Field(..., description="Unique ID of the feedback config.")
    type: FeedbackType = Field(
        ..., description="Feedback mechanism type (e.g., thumbs, star, text)."
    )
    question: Optional[str] = Field(
        None, description="Question to show user for qualitative feedback."
    )
    prompt: Optional[Prompt] = Field(
        None, description="Prompt object used to generate a follow-up based on feedback."
    )


class Condition(BaseModel):
    """Conditional logic for branching execution within a flow."""

    if_var: str = Field(..., description="ID of the variable to evaluate.")
    equals: Optional[Union[str, int, float, bool]] = Field(
        None, description="Match condition for equality check."
    )
    exists: Optional[bool] = Field(
        None, description="Condition to check existence of a variable."
    )
    then: List['Step'] = Field(
        ..., description="List of step objects to run if condition matches."
    )
    else_: Optional[List['Step']] = Field(
        None,
        alias="else",
        description="Optional list of step objects to run if condition fails.",
    )


class Step(BaseModel):
    """A single execution step within a flow (e.g., prompt, tool call, or memory update)."""

    id: str = Field(..., description="Unique ID of the step.")
    input_vars: Optional[List[Input]] = Field(
        None, description="Input objects required by this step."
    )
    output_vars: Optional[List[Output]] = Field(
        None, description="Output objects where results are stored."
    )
    component: Optional[Union[
        Prompt, 
        Tool, 
        ToolProvider, 
        BaseRetriever, 
        'Flow'
    ]] = Field(
        None, description="Component object to invoke (e.g., prompt, tool, retriever)."
    )


class Flow(Step):
    """A flow represents the full composition of steps a user or system interacts with."""

    mode: FlowMode = Field(..., description="Interaction mode for the flow.")
    inputs: Optional[List[Input]] = Field(
        None, description="Input objects accepted by the flow."
    )
    outputs: Optional[List[Output]] = Field(
        None, description="Output objects produced by the flow."
    )
    steps: List[Union[Step, 'Flow']] = Field(
        ..., description="List of step objects or nested flow objects."
    )
    conditions: Optional[List[Condition]] = Field(
        None, description="Optional conditional logic within the flow."
    )
    memory: Optional[List[Memory]] = Field(
        None, description="List of memory objects to include (chat mode only)."
    )


class QTypeSpec(BaseModel):
    """
    The top-level definition of a resolved QType specification.

    This class represents the full configuration of a generative AI application,
    including models, inputs, prompts, tools, flows, and supporting infrastructure,
    with all ID references resolved to actual object references.

    Only one `QTypeSpec` should exist per resolved specification.
    """

    version: str = Field(
        ..., description="Version of the QType specification schema used."
    )
    models: Optional[List[Model]] = Field(
        None,
        description="List of generative model objects available for use, including their providers and inference parameters.",
    )
    inputs: Optional[List[Input]] = Field(
        None, description="User-facing input objects exposed by the application."
    )
    prompts: Optional[List[Prompt]] = Field(
        None,
        description="Prompt template objects used in generation steps or tools, with resolved input and output references.",
    )
    retrievers: Optional[List[BaseRetriever]] = Field(
        None,
        description="Document retriever objects used to fetch context from indexes (e.g., vector search, keyword search).",
    )
    tools: Optional[List[ToolProvider]] = Field(
        None,
        description="Tool provider objects with optional OpenAPI specs, exposing callable tools for the model.",
    )
    flows: Optional[List[Flow]] = Field(
        None,
        description="Entry point flow objects to application logic. Each flow defines an executable composition of steps.",
    )
    feedback: Optional[List[Feedback]] = Field(
        None,
        description="Feedback configuration objects for collecting structured or unstructured user reactions to outputs.",
    )
    memory: Optional[List[Memory]] = Field(
        None,
        description="Session-level memory context objects, only used in chat-mode flows to persist state across turns.",
    )
    auth: Optional[List[AuthorizationProvider]] = Field(
        None,
        description="Authorization provider objects and credentials used to access external APIs or cloud services.",
    )

