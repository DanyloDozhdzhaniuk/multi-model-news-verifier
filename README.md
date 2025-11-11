# News Verification AI

A web app for **verifying news articles** using multiple AI models and an **internet-based fact-checking system**. This tool helps assess the reliability of news by comparing it with real world sources and analyzing semantic consistency.

---

### Link to the fine-tuned BERT model (you can read about it more there too): https://huggingface.co/v0lt/News_Reliability_BERT_fine_tuned

---

## Features

- **Semantic similarity check** – Measures similarity between user input and verified news using Sentence Transformers and [World News API](https://worldnewsapi.com/)
- **BERT-based reliability prediction** – Fine-tuned model to evaluate the trustworthiness of news text
- **Natural Language Inference (NLI)** – Detects contradictions, neutral statements, or entailments between user input and reference news
- **Summarization** – Summarizes long texts for faster analysis and compatability with other AI models and tools
- **Responsive web interface** – Interactive and User Friendly UI with live reliability score feedback

---

## Demo

<p align="center">
  <img src="preview.gif"/>
</p>

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
