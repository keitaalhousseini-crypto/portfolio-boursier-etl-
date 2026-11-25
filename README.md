# Portfolio Boursier — Automated Financial Analytics

**End-to-End Data Engineering & Financial Analytics Project**

Python · pandas · PostgreSQL · Docker Compose · pgAdmin 4 · Metabase · pytest

## Project Objective

Build a reproducible financial data platform to collect historical stock prices, validate market data, calculate portfolio performance and risk indicators, and visualize results through an interactive Business Intelligence dashboard.

## Architecture

Market Data (Yahoo Finance / Local Cache / Synthetic Demo) → Python ETL → Data Quality → PostgreSQL → Metabase

## Assets

AAPL, MSFT, NVDA, AMZN, GOOGL, JPM, UBS and SPY (benchmark).

## Data Modes

- **Online:** Historical prices retrieved using yfinance.
- **Cache:** Previously validated historical data stored locally.
- **Demo:** Reproducible synthetic data for offline testing.

Synthetic data is explicitly identified and never represented as real market data.

## Project Status

Phase 1 — Development environment setup.

Implementation, validation results and dashboard screenshots will be added progressively.