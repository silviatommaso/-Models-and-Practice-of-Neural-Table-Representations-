# -Models-and-Practice-of-Neural-Table-Representations-

This repository contains the implementation and evaluation of two paradigms for relational question answering over structured data:

- **Text-to-SQL**
- **Direct Table QA**

The study compares the performance of different Large Language Models under multiple prompting strategies, including zero-shot, few-shot, and attribute-enhanced settings.

---

## 🧠 Overview

The goal of this project is to analyze how LLMs behave when interacting with relational databases, both by generating SQL queries (Text-to-SQL) and by directly reasoning over serialized table data (Direct QA).

The experiments are conducted on a subset of the Spider benchmark (`book_1.sqlite` dataset), and evaluated using execution-based metrics.

---

## API Configuration

Create a .config file based on the .config.example and add your API keys.

---

## Local paths configuration

Create a .env file based on the .env.example and add your sqlite database and annotation.json local path.
