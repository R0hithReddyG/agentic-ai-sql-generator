from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from database.seed import seed_database
from services.query_service import QueryRequest, process_query

st.set_page_config(page_title="Agentic SQL Generator", layout="wide")
st.title("Agentic SQL Query Generator")

if "initialized" not in st.session_state:
    seed_database()
    st.session_state.initialized = True

if "history" not in st.session_state:
    st.session_state.history = []

question = st.text_area("Ask a question about your data:", height=80, placeholder="e.g., What are the top 5 customers by total order amount?")

col1, col2 = st.columns([1, 4])
with col1:
    run_btn = st.button("Run Query", type="primary", use_container_width=True)
with col2:
    if st.button("Clear History"):
        st.session_state.history = []

if run_btn and question.strip():
    with st.spinner("Agent is thinking..."):
        request = QueryRequest(question=question.strip())
        response = process_query(request)
        st.session_state.history.insert(0, {
            "question": question,
            "response": response,
        })

for entry in st.session_state.history[:20]:
    q = entry["question"]
    r = entry["response"]

    with st.expander(f"**Q:** {q}", expanded=True):
        status_color = "green" if r.status == "completed" else "red" if r.status == "failed" else "orange"
        st.markdown(f"**Status:** :{status_color}[{r.status}]")

        if r.answer:
            st.markdown(f"**Answer:** {r.answer}")

        if r.sql:
            st.code(r.sql, language="sql")

        if r.results:
            st.markdown(f"**Results** ({r.row_count} rows):")
            import pandas as pd
            df = pd.DataFrame(r.results)
            st.dataframe(df, use_container_width=True)

        if r.trace:
            st.markdown("**Execution Trace:**")
            for step in r.trace:
                icon = "✅" if step.get("success") else "❌"
                st.text(f"  {icon} {step.get('tool_name')} ({step.get('duration_ms', 0):.1f}ms)")

        if r.errors:
            st.markdown("**Errors:**")
            for err in r.errors:
                st.warning(f"[{err.get('phase')}] {err.get('message')}")

        if r.corrections:
            st.markdown("**Corrections:**")
            for corr in r.corrections:
                st.info(f"Attempt {corr.get('attempt_number')}: {corr.get('strategy')}")

        if r.synthesized_response:
            with st.popover("View Full Response JSON"):
                st.json(r.synthesized_response)
