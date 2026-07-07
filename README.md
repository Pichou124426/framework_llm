# RAG Offensive Framework

Framework de simulation d'attaques offensives ciblant l'étape de retrieval des pipelines RAG (Retrieval-Augmented Generation), développé dans le cadre d'un stage en sécurité des infrastructures IA.

## Objectif

Documenter et simuler les vecteurs d'attaque connus visant le retriever d'une architecture RAG, à des fins de compréhension pratique et de préparation de mesures de défense.

## Périmètre

Ce framework couvre exclusivement les attaques ciblant l'étape de retrieval (base vectorielle, mécanismes de similarité, embeddings). L'indexation et la génération ne sont pas traitées, sauf lorsqu'une attaque initiée à l'indexation a un impact direct sur le retrieval.
