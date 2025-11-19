#!/usr/bin/env python3
"""
Tourism Database - Colombia Travel Search System
Using Polars instead of Pandas (Windows-safe, no binary issues)
"""

import polars as pl
from fuzzywuzzy import fuzz, process
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TourismDatabase:
    def __init__(self, csv_file="data/tourism_data.csv"):
        self.df = None
        self.departamentos = set()
        self.tipos = set()
        self.load_data(csv_file)

    def load_data(self, csv_file):
        try:
            # Load with Polars
            self.df = pl.read_csv(csv_file, encoding="utf8")

            # Convert price column (if exists)
            if "precio_estimado" in self.df.columns:
                self.df = self.df.with_columns(
                    pl.col("precio_estimado").cast(pl.Float64, strict=False)
                )

            # Fill null values
            self.df = self.df.fill_null("")

            # Save unique departments and types
            self.departamentos = set(self.df["departamento"].to_list())
            self.tipos = set(self.df["tipo"].to_list())

            # Build search_text
            self.df = self.df.with_columns(
                (
                    pl.col("destino").str.to_lowercase()
                    + " "
                    + pl.col("departamento").str.to_lowercase()
                    + " "
                    + pl.col("tipo").str.to_lowercase()
                    + " "
                    + pl.col("actividades").str.to_lowercase()
                    + " "
                    + pl.col("descripcion").str.to_lowercase()
                ).alias("search_text")
            )

            logger.info(f"Loaded {self.df.height} destinos turísticos")

        except Exception as e:
            logger.error(f"Error loading tourism data: {e}")
            raise

    def search(self, query: str, max_results=8) -> Tuple[List[Dict], str]:
        """Search destinations using fuzzy and exact matching"""
        if not query.strip():
            return self.featured_destinations(max_results), "Destinos destacados de Colombia"

        query = query.lower()

        # --- Exact match ---
        exact = self.df.filter(pl.col("search_text").str.contains(query))
        if exact.height > 0:
            return self._format(exact.head(max_results)), f"Resultados exactos para '{query}'"

        # --- Fuzzy match destino ---
        destinos_lower = [d.lower() for d in self.df["destino"].to_list()]
        matches = process.extract(query, destinos_lower, limit=max_results)
        good = [m[0] for m in matches if m[1] > 60]

        fuzzy = self.df.filter(pl.col("destino").str.to_lowercase().is_in(good))
        if fuzzy.height > 0:
            return self._format(fuzzy), f"Destinos similares a '{query}'"

        # --- Departments ---
        matches = process.extract(query, list(self.departamentos), limit=3)
        good = [m[0] for m in matches if m[1] > 60]

        if good:
            dept = self.df.filter(pl.col("departamento").is_in(good))
            if dept.height > 0:
                return self._format(dept), f"Destinos en {good[0]}"

        # --- Types ---
        matches = process.extract(query, list(self.tipos), limit=3)
        good = [m[0] for m in matches if m[1] > 60]

        if good:
            tipo = self.df.filter(pl.col("tipo").is_in(good))
            if tipo.height > 0:
                return self._format(tipo), f"Destinos del tipo {good[0]}"

        # --- Fallback full text ---
        fallback = self.df.filter(pl.col("search_text").str.contains(query)).head(max_results)
        if fallback.height > 0:
            return self._format(fallback), f"Resultados de búsqueda para '{query}'"

        return self.featured_destinations(max_results), (
            f"No encontré coincidencias para '{query}', pero mira estos destinos populares:"
        )

    def featured_destinations(self, max_results=8):
        sample_df = self.df.sample(n=min(max_results, self.df.height))
        return self._format(sample_df)

    def _format(self, df_subset: pl.DataFrame):
        destinos = []

        for row in df_subset.to_dicts():
            destinos.append(
                {
                    "name": row.get("destino", ""),
                    "department": row.get("departamento", ""),
                    "type": row.get("tipo", ""),
                    "price": row.get("precio_estimado", ""),
                    "description": row.get("descripcion", ""),
                    "activities": row.get("actividades", ""),
                    "climate": row.get("clima", ""),
                    "season": row.get("temporada_ideal", ""),
                }
            )

        return destinos


# GLOBAL INSTANCE
tourism_db = TourismDatabase()


def get_tourism_db():
    return tourism_db
