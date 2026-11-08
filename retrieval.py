from config import TOP_K, RELEVANCE_THRESHOLD


def retrieve_documents(vectorstore, question):

    # STEP 1: SEARCH RELEVANT DOCUMENTS

    matches = vectorstore.similarity_search_with_score(
        query=question,
        k=TOP_K
    )

    if not matches:

        print("\nNo relevant documents found.")

        return None


    # STEP 2: RETRIEVAL DIAGNOSTICS

    print("\nRetrieval diagnostics:")

    for rank, (doc, distance) in enumerate(
        matches,
        start=1
    ):

        print(
    
        f"{rank}. Cosine distance: {distance:.4f}"
        )    
        print(f"   Source: {doc.metadata.get('source')}")
        print(f"   Page: {doc.metadata.get('page')}")
        print(f"   Content: {doc.page_content[:500]}")

        


    best_distance = float(matches[0][1])

    print(
        f"\nBest cosine distance: {best_distance:.4f}"
    )


    # STEP 3: RELEVANCE CHECK

    if best_distance > RELEVANCE_THRESHOLD:

        print(
            "\nI don't know based on the provided documents."
        )

        print(
            "No sufficiently relevant information found."
        )

        return None


    # STEP 4: EXTRACT DOCUMENTS

    results = [
    doc
    for doc, distance in matches
    if distance <= RELEVANCE_THRESHOLD
]


    # STEP 5: PREPARE CONTEXT

    context = "\n\n".join(
        doc.page_content for doc in results
    )


    print("DEBUG: Context prepared successfully", flush=True)
    print("DEBUG: Returning results to app.py", flush=True)
    return context, results