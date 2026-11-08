
from transformers import pipeline

from config import LLM_MODEL_NAME
from ingestion import create_or_update_vectorstore
from retrieval import retrieve_documents


REFUSAL = "I don't know based on the provided document."


def clean_answer(text):
    """Clean the generated response."""

    if not isinstance(text, str):
        return ""

    text = text.split("<|im_end|>")[0]
    text = text.split("<|endoftext|>")[0]

    return " ".join(text.split()).strip()


def display_sources(results):
    """Display unique source documents and page numbers."""

    print("\nSources:")

    shown_sources = set()

    for doc in results:

        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")

        source_key = (source, page)

        if source_key in shown_sources:
            continue

        shown_sources.add(source_key)

        if page is not None:
            print(f"- {source} (Page {page + 1})")
        else:
            print(f"- {source}")


def generate_answer(generator, question, context):
    """Generate an answer using only the retrieved document context."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict document-grounded question answering assistant. "

                "SOURCE RULES:\n"
                "1. Use ONLY facts explicitly stated in the DOCUMENT CONTEXT.\n"
                "2. Never use outside knowledge, assumptions, or general knowledge.\n"
                "3. Do not add examples, applications, definitions, or explanations "
                "that are not present in the context.\n"
                "4. Do not invent details to make an answer more complete.\n"
                "5. Preserve the original meaning and factual accuracy of the document.\n"
                "6. Do not change important technical terms or facts.\n"

                "ANSWER RULES:\n"
                "1. Answer the exact question asked.\n"
                "2. Keep the answer concise and factual.\n"
                "3. Use only the relevant information from the context.\n"
                "4. If only partial information is available, answer only that part.\n"
                "5. If the context does not contain enough information to answer, "
                f"respond exactly: {REFUSAL}\n"

                "Do not include unsupported claims."
            )
        },
        {
            "role": "user",
            "content": (
                f"DOCUMENT CONTEXT:\n{context}\n\n"
                f"QUESTION:\n{question}\n\n"
                "Answer using only the facts in the document context."
            )
        }
    ]

    prompt = generator.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    response = generator(
        prompt,
        max_new_tokens=200,
        do_sample=False,
        return_full_text=False
    )

    answer = clean_answer(response[0]["generated_text"])

    return answer if answer else REFUSAL


def main():

    # STEP 1: CONNECT TO VECTOR DATABASE

    print("\nConnecting to vector database...")

    vectorstore = create_or_update_vectorstore()

    if vectorstore is None:
        raise RuntimeError("Vector database connection failed.")

    print("Vector database connected successfully.")


    # STEP 2: LOAD QWEN MODEL

    print("\nLoading Qwen model...")

    generator = pipeline(
        "text-generation",
        model=LLM_MODEL_NAME
    )

    print("\nRAG Assistant is ready!")


    # STEP 3: INTERACTIVE QUESTION LOOP

    while True:

        question = input(
            "\nAsk your question (or type exit to stop): "
        ).strip()

        if question.lower() in ("exit", "quit"):

            print("\nThank you for using RAG Assistant!")
            break

        if not question:

            print("\nPlease enter a question.")
            continue


        # STEP 4: RETRIEVE RELEVANT DOCUMENTS

        try:

            retrieved = retrieve_documents(
                vectorstore,
                question
            )

        except Exception as error:

            print(f"\nRetrieval error: {error}")
            continue


        if retrieved is None:

            print("\nAnswer:")
            print(REFUSAL)
            continue


        if not isinstance(retrieved, tuple) or len(retrieved) != 2:

            print("\nInvalid retrieval result.")
            continue


        context, results = retrieved

        if not context or not context.strip():

            print("\nAnswer:")
            print(REFUSAL)
            continue


        # STEP 5: GENERATE ANSWER

        print("\nGenerating answer...", flush=True)

        try:

            answer = generate_answer(
                generator,
                question,
                context
            )

        except Exception as error:

            print(f"\nGeneration error: {error}")
            continue


        # STEP 6: DISPLAY ANSWER

        print("\nAnswer:")
        print(answer)


        # STEP 7: DISPLAY SOURCES

        display_sources(results)


if __name__ == "__main__":
    main()
