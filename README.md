# 👑 Restaurant Data AI — Plateforme d'Analyse & Concierge IA

Bienvenue sur la plateforme **Restaurant Data AI**, une solution complète d'ingestion de données, d'analyse statistique, de prédiction par Machine Learning et de conciergerie intelligente basée sur une architecture **RAG Text-to-SQL**.

---

## 📋 Table des Matières

1. [À propos du Projet](#-à-propos-du-projet)
2. [Documentation Technique](#-documentation-technique)
   - [Architecture du Système](#1-architecture-du-système)
   - [Technologies Utilisées](#2-technologies-utilisées)
   - [Structure du Projet](#3-structure-du-projet)
3. [Documentation d'Installation](#-documentation-dinstallation)
   - [Prérequis](#1-prérequis)
   - [Installation étape par étape](#2-installation-étape-par-étape)
   - [Variables d'Environnement](#3-variables-denvironnement)
4. [Lancement de l'Application](#-lancement-de-lapplication)
5. [Code Source & Architecture des Modules](#-code-source--architecture-des-modules)

---

## 💡 À propos du Projet

Ce projet a été développé dans le cadre d'un projet d'ingénierie et de stage. Il permet de :
- Centraliser et collecter les données du secteur de la restauration à Casablanca et au Maroc.
- Stocker et structurer ces données dans une base relationnelle robuste.
- Visualiser des Indicateurs Clés de Performance (KPI) via un tableau de bord interactif.
- Consulter un **Concierge IA** capable de traduire les questions en langage naturel en requêtes SQL exécutées directement sur la base de données.

---

## 🛠️ Documentation Technique

### 1. Architecture du Système

L'application repose sur une architecture découplée et modulaire en couches :

```text
┌─────────────────────────┐
│   Sources de Données    │
└────────────┬────────────┘
             │ (Scraping / Cleaning)
             ▼
┌─────────────────────────┐
│ Base PostgreSQL         │ ◄──┐
└────────────┬────────────┘    │
             │                 │ Requêtes SQL (SQLAlchemy)
             ▼                 │
┌─────────────────────────┐    │
│ Pipeline RAG            ├────┘
│ (llm/rag.py)            │
└────────────┬────────────┘
             │ (API Google GenAI)
             ▼
┌─────────────────────────┐
│ Tableau de Bord         │
│ (Streamlit Interface)   │
└─────────────────────────┘