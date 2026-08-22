# AI Job Research & Matching Platform

An AI-powered job research and matching platform that helps users discover relevant job opportunities using natural-language search, semantic matching, personalized recommendations, and resume-based job matching.

The application combines a React frontend with a FastAPI backend, PostgreSQL for structured job data, and Qdrant for vector-based semantic search.

---

## 📌 Project Overview

The goal of this project is to build an intelligent job discovery platform that goes beyond traditional keyword-based job searching.

Instead of requiring users to search using exact keywords, the platform allows them to describe what they are looking for naturally.

For example:

> "I am looking for remote Python Data Scientist jobs with Machine Learning experience."

The system processes the request, searches the job dataset, calculates relevance, and presents the most suitable opportunities.

The platform provides four major experiences:

1. **Jobs**
2. **AI Job Assistant**
3. **Recommendations**
4. **Resume Match**

---

# 🚀 Key Features

## 1. Job Search

The Jobs section allows users to browse and search through the available job dataset.

Users can search based on information such as:

- Job title
- Company
- Location
- Skills
- Experience
- Employment type
- Other job-related attributes

The backend retrieves relevant jobs from PostgreSQL.

---

## 2. AI Job Assistant

The AI Job Assistant allows users to search for jobs using natural language.

Example:

```text
Find remote Python developer jobs