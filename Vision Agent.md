# Vision Agent

The Vision Agent in OmniBrain is specialized in processing and interpreting visual information embedded within documents, such as charts, graphs, and diagrams. It leverages advanced Vision-Language Models (VLMs) to extract data, identify trends, and provide insights from visual content.

## Role and Responsibilities

The primary role of the Vision Agent is to enable OmniBrain to understand and reason over visual data. Its key responsibilities include:

1.  **Image Extraction and Preprocessing:** The agent identifies and extracts relevant images from documents. It may perform preprocessing steps like cropping, resizing, or enhancing image quality to optimize for VLM input.
2.  **Visual Data Interpretation:** It utilizes a VLM (e.g., GPT-4o with vision capabilities, LLaVA) to analyze the visual content. This involves tasks such as:
    *   Reading text from images (OCR).
    *   Extracting numerical data from bar charts, line graphs, and tables within images.
    *   Identifying trends, patterns, and anomalies in visual representations.
    *   Answering natural language questions about the image content.
3.  **Contextual Reasoning:** The agent can combine visual information with textual context provided by the Supervisor Agent to perform more sophisticated reasoning, such as comparing a visual trend with a textual description.
4.  **Result Formatting:** It translates the visual insights into a structured or natural language format that can be easily integrated into the Supervisor Agent's synthesis process. This often includes quoting specific data points or describing visual trends.

## Implementation Details

The Vision Agent relies heavily on the capabilities of a powerful Vision-Language Model. The interaction with the VLM typically involves sending the image (or a reference to it) along with a textual prompt that guides the VLM's analysis.

### Key Components:

*   **Image Processing Library:** Libraries like Pillow (PIL) or OpenCV for image manipulation and preprocessing.
*   **VLM API Integration:** Integration with a VLM service (e.g., OpenAI's API for GPT-4o, or a local deployment of LLaVA). The agent constructs prompts that effectively guide the VLM to extract the desired information.
*   **Image Embedding (Optional):** For multi-modal retrieval, images might also be embedded using models like CLIP and stored in the vector database, allowing the Search Agent to retrieve relevant images based on semantic similarity.

## Example Workflow

1.  **Supervisor Agent Request:** The Supervisor Agent receives a query like "What was the projected growth for Q2 based on the chart in the presentation?" and identifies that a visual analysis is required.
2.  **Image Retrieval:** The Vision Agent (or the Search Agent, if images are indexed) retrieves the relevant chart image from the document or vector database.
3.  **VLM Analysis:** The Vision Agent sends the image and a prompt (e.g., "Extract the projected growth percentage for Q2 from this chart.") to the VLM.
4.  **Insight Extraction:** The VLM processes the image, reads the chart, and returns the projected growth percentage.
5.  **Return to Supervisor:** The Vision Agent formats this insight and returns it to the Supervisor Agent, which can then use it to compare with actual growth data from the SQL Agent or Search Agent.
