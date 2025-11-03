## WORKED
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

json_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "rating": {
            "type": "number"
        }
    },
    "required": [
        "title",
        "rating"
    ]
}

prompt = (f"Return the title and the rating based on the following movie review according to this JSON schema: {str(json_schema)}.\n"
          f"Review: Inception is a really well made film. I rate it four stars out of five.")
messages = [
    {"role": "user", "content": prompt},
]
response = client.chat.completions.create(
    # model="meta/llama-3.1-70b-instruct",
    model = "nvidia/llama-3.1-nemotron-nano-8b-v1",
    messages=messages,
    extra_body={"nvext": {"guided_json": json_schema}},
    stream=False
)
assistant_message = response.choices[0].message.content
print(assistant_message)
