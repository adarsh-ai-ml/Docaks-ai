import hashlib

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import (
    PDF_DIR,
    DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME
)


def create_or_update_vectorstore():

    # STEP 1: FIND ALL PDF FILES

    print("\nSearching for PDF documents...")

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF files found inside the data folder."
        )

    print(f"PDF files found: {len(pdf_files)}")


    # STEP 2: LOAD ALL PDFs AND GENERATE FINGERPRINTS

    all_docs = []

    current_hashes = {}

    for pdf_file in pdf_files:

        print(f"\nLoading: {pdf_file.name}")

        file_hash = hashlib.sha256(
            pdf_file.read_bytes()
        ).hexdigest()

        current_hashes[str(pdf_file)] = file_hash

        loader = PyPDFLoader(str(pdf_file))

        loaded_docs = loader.load()

        for doc in loaded_docs:

            doc.metadata["file_hash"] = file_hash

        all_docs.extend(loaded_docs)

    print(f"\nTotal pages loaded: {len(all_docs)}")

    if not all_docs:
        raise ValueError(
            "No PDF content could be loaded."
        )


    # STEP 3: SPLIT DOCUMENTS INTO CHUNKS

    print("\nSplitting documents...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(all_docs)

    if not chunks:
        raise ValueError("No text chunks were created.")

    print(f"Total chunks: {len(chunks)}")


    # STEP 4: LOAD EMBEDDING MODEL

    print("\nLoading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )


    # STEP 5: CONNECT TO CHROMA DATABASE

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_PATH,
        collection_metadata={"hnsw:space": "cosine"}
    )


    # STEP 6: SMART DATABASE SYNCHRONIZATION

    print("\nChecking existing database...")

    existing_records = vectorstore.get(
        include=["metadatas"]
    )

    existing_ids = existing_records.get("ids", [])

    existing_metadatas = existing_records.get(
        "metadatas", []
    )

    existing_hashes = {}

    existing_ids_by_source = {}


    # Read existing database information

    for record_id, metadata in zip(
        existing_ids,
        existing_metadatas
    ):

        metadata = metadata or {}

        source = metadata.get("source")

        file_hash = metadata.get("file_hash")

        if source:

            existing_ids_by_source.setdefault(
                source, []
            ).append(record_id)

            if file_hash:

                existing_hashes[source] = file_hash


    # Remove records of deleted PDFs

    for old_source, old_ids in existing_ids_by_source.items():

        if old_source not in current_hashes:

            vectorstore.delete(ids=old_ids)

            print(f"Removed deleted PDF: {old_source}")


    # Add new PDFs or update modified PDFs

    added_chunks = 0

    for pdf_path, file_hash in current_hashes.items():

        # Skip unchanged PDFs

        if existing_hashes.get(pdf_path) == file_hash:

            print(f"Already up to date: {pdf_path}")

            continue


        # Remove old records if PDF has changed

        old_ids = existing_ids_by_source.get(
            pdf_path, []
        )

        if old_ids:

            vectorstore.delete(ids=old_ids)

            print(f"Updated changed PDF: {pdf_path}")

        else:

            print(f"Indexing new PDF: {pdf_path}")


        # Select chunks belonging to this PDF

        pdf_chunks = [
            chunk
            for chunk in chunks
            if chunk.metadata.get("source") == pdf_path
        ]


        # Add updated chunks to database

        if pdf_chunks:

            vectorstore.add_documents(
                documents=pdf_chunks
            )

            added_chunks += len(pdf_chunks)

        else:

            print(f"Warning: No chunks found for {pdf_path}")


    print("\nVector database synchronization completed!")

    print(f"PDF files detected: {len(pdf_files)}")

    print(f"New/updated chunks indexed: {added_chunks}")

    return vectorstore