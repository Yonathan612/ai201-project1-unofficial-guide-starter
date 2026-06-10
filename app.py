import gradio as gr

from rag import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    try:
        result = ask(question)
        sources = "\n".join(f"• {s}" for s in result["sources"])
        return result["answer"], sources
    except ValueError as e:
        return str(e), ""
    except Exception as e:
        return f"Something went wrong: {e}", ""


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask questions about CS professors and courses — answers are grounded "
        "in student review documents with source citations."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which professor is best for a beginner in programming?",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
