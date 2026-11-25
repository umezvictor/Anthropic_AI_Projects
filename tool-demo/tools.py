"""The tool definitions. One tool with an action parameter, then three tools."""

# ONE TOOL. Three jobs behind one name, picked with an action parameter.
ONE_TOOL = [
    {
        "name": "analyze_document",
        "description": (
            "Runs one of three jobs on a contract from the store. "
            "Set action to extract to get the values of the fields you list. "
            "Set action to summarize to get a summary, and set length. "
            "Set action to verify to check one claim, and put the claim in claim. "
            "Returns field values, a summary, or a verdict, depending on the action."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string"},
                "action": {"type": "string", "enum": ["extract", "summarize", "verify"]},
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["payment_terms", "late_fee", "renewal",
                                 "termination_notice", "liability_cap"],
                    },
                },
                "length": {"type": "string", "enum": ["short", "detailed"]},
                "claim": {"type": "string"},
            },
            "required": ["document_id", "action"],
            "additionalProperties": False,
        },
    }
]

# THREE TOOLS. One job each. Each tool requires only what its job needs.
THREE_TOOLS = [
    {
        "name": "extract_data_points",
        "description": (
            "Reads a contract from the store and returns the exact value of each "
            "field you list, with the clause number it came from. "
            "Use it when the user asks what the contract says about a topic. "
            "This includes yes or no questions, such as: Does the contract renew on its own? "
            "Do not use it for an overview of the whole contract. "
            "Do not use it when the user states a claim from another source and asks you to check it."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string"},
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["payment_terms", "late_fee", "renewal",
                                 "termination_notice", "liability_cap"],
                    },
                },
            },
            "required": ["document_id", "fields"],
            "additionalProperties": False,
        },
    },
    {
        "name": "summarize_content",
        "description": (
            "Reads a contract from the store and returns a summary in plain language. "
            "Use it when the user wants an overview of the whole contract. "
            "Do not use it for one value, such as a fee, a date or a notice period. "
            "Set length to short for a few sentences, or detailed for one paragraph per section."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string"},
                "length": {"type": "string", "enum": ["short", "detailed"]},
            },
            "required": ["document_id", "length"],
            "additionalProperties": False,
        },
    },
    {
        "name": "verify_claim_against_source",
        "description": (
            "Checks one claim against the text of a contract from the store. "
            "Returns a verdict of supported, contradicted or not found, and the "
            "sentence from the contract behind the verdict. "
            "Use it only when the user states a claim from another source, such as "
            "an email or a draft, and asks you to check it. "
            "Do not use it for plain questions about the contract, even yes or no questions. "
            "Put the claim in the claim field as one sentence."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string"},
                "claim": {"type": "string"},
            },
            "required": ["document_id", "claim"],
            "additionalProperties": False,
        },
    },
]

# SHORT VERSION. Same names, same schemas. Only the description changes.
SHORT_DESCRIPTIONS = {
    "extract_data_points": "Extracts data points from a contract.",
    "summarize_content": "Summarizes a contract.",
    "verify_claim_against_source": "Verifies a claim against a contract.",
}

SHORT_TOOLS = [
    dict(tool, description=SHORT_DESCRIPTIONS[tool["name"]]) for tool in THREE_TOOLS
]
