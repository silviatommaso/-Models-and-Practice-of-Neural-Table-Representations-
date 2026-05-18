# -Models-and-Practice-of-Neural-Table-Representations-

This repository contains the implementation and evaluation of two paradigms for relational question answering over structured data:

- **Text-to-SQL**
- **Direct Table QA**

The study compares the performance of different Large Language Models under multiple prompting strategies, including zero-shot, few-shot, and attribute-enhanced settings.

---

## Overview

The goal of this project is to analyze how Large Language Models (LLMs) interact with relational databases, both through SQL query generation (Text-to-SQL) and direct reasoning over serialized tabular data (Direct QA).

To this end, we implement a unified pipeline supporting both paradigms and assess their performance using data-centric metrics combined with a qualitative error analysis across different query types and database schemas. Experiments are conducted under multiple prompt configurations, including zero-shot, few-shot, and attribute-enhanced settings, to investigate their impact on model performance.

The experiments are conducted on a subset of the Spider benchmark (`book_1.sqlite` dataset), and evaluated using execution-based metrics.

---

## Installation

1. Get a free API Key at https://groq.com/
2. Clone the repo
   ```
   git clone https://github.com/silviatommaso/-Models-and-Practice-of-Neural-Table-Representations-.git
   ```
3. Create a .config file based on the .config.example and add your API keys
   ```
   API_KEY = "your_api_key_here"
   ```
4. Create a .env file based on the .env.example and add your sqlite database, annotation.json, examples.json and attribute_desc.json       local path.
   ```
   DB_PATH = "your_database_local_path_here"
   ANNOTATION_PATH = "your_annotation_local_path_here"
   EXAMPLES_PATH = "your_fewshot_examples_local_path_here"
   ATTRIBUTE_DESC_PATH = "your_attribute_descriptions_local_path_here"
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```
   git remote set-url origin https://github.com/silviatommaso/-Models-and-Practice-of-Neural-Table-Representations-.git
   git remote -v # confirm the changes
   ```

---

## Usage

The default experimental setting uses a **zero-shot prompting** paradigm.

To test the alternative configurations, edit the `llm_requests.py` file and modify the following boolean parameters:

```python
USE_ATTRIBUTES = True | False
USE_EXAMPLES = True | False
```

These settings enable different prompting strategies:

USE_ATTRIBUTES = True → attribute-enhanced prompting
USE_EXAMPLES = True → few-shot prompting
both set to False → zero-shot prompting


### Rate Limit Handling

If token-per-minute rate limits occur, increase the pause intervals in llm_requests.py by modifying:

```python
PAUSE_BETWEEN_MODELS 
PAUSE_BETWEEN_QUERIES 
```
Increasing these values adds a longer delay between API requests and helps avoid rate-limit errors.


### Output Management

The main execution script of the project is `pipeline.py`.

To avoid overwriting experiment results, it is recommended to modify the output path of the generated JSON files in pipeline.py, according to the selected configuration.

This ensures that results from different experimental settings (zero-shot, few-shot, and attribute-enhanced) are stored separately and can be compared safely.

---

## Acknowledgements

This project makes use of the following resources:

- **Spider dataset**: https://yale-lily.github.io/spider
- **Groq API**: https://groq.com/

We thank the creators of these resources for their contributions to research and benchmarking in this field.

## Contact

Silvia Tommaso - https://www.linkedin.com/in/silvia-tommaso-9476a2398/ - silvia.tommaso18112002@gmail.com
