from langchain_core.prompts import PromptTemplate


def get_prompt(parser):

    template = """You are a helpful assistant.
      Answer the question using ONLY the context below.
      If the answer is not in the context, say "I don't have enough information to answer that."

       Context:
         {context}

      Question: {input}

      {format_instructions}"""

    return PromptTemplate(
        input_variables=["context", "input"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
        template=template
    )