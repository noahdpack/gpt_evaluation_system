import streamlit as st


def render_dashboard(result_list):
    for result in result_list:
        overall_score = result["final_score"]
        
        if result["passed"]:
            test_status = "Passed"
        else: 
            test_status = "Failed"

        root_label = (
            f"{result["id"]} - {result["name"]} | " 
            f"Status: {test_status} | "
            f"Overall Score: {overall_score}/5"
        )

        with st.expander(root_label, expanded=False):
            st.markdown("### Overall Evaluation")
            st.markdown(f"**Overall score:** {overall_score}")
            st.write(result["overall_judge_explanation"])

            st.divider()

            st.markdown("### Dimension Scores")

            #---LLM JUDGE DIMENSIONS---

            for dimension_name, dimension in result["dimension_scores"].items():
                dimension_score = dimension["score"]
                
                dimension_label = (
                    f"{dimension_name.title()}: {dimension_score}/5"
                )

                with st.expander(dimension_label):
                    st.markdown(f"**Score:** {dimension_score}/5")

                    st.markdown("**Bot Response**:")
                    st.info(dimension["model_response"])

                    st.markdown("**LLM Judge Explanation**:")
                    st.info(dimension["explanation"])


            #--- DETERMINISTIC CHECK DIMENSIONS---

            relevant_language_score = result["deterministic_checks"]["relevant_language_results"]["score"]

            relevant_language_label = (
                f"Relevant Language: {relevant_language_score}/5"
            )

            with st.expander(relevant_language_label):
                st.markdown(f"f**Score:** {relevant_language_score}/5")

                st.markdown("**Score Explanation:**")
                st.info(result["deterministic_checks"]["relevant_language_results"]["explanation"])

            severity_score = result["deterministic_checks"]["severity_results"]["score"]

            severity_label = (
                f"Severity: {severity_score}/5"
            )

            with st.expander(severity_label):
                st.markdown(f"**Score:** {severity_score}/5")

                st.markdown(f"**Score Explanation:**")
                st.info(result["deterministic_checks"]["severity_results"]["explanation"])


            #---HARD GATES---
            for gate_name, gate_result in result["hard_gates"].items():
                if gate_result["passed"]:
                    status = "passed"
                else:
                    status = "failed"
                
                gate_label = (
                    f"{gate_name.title()}: {status}"
                )

                with st.expander(gate_label):
                    st.markdown(f"**Status**: {status}")

                    st.markdown(f"**Status Explanation:**")
                    st.info(gate_result["explanation"])
