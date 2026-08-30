import streamlit as st
from supabase import create_client

# 从 Streamlit Secrets 读取凭证
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

st.set_page_config(page_title="微信群知识库 & 共创 Q&A", layout="wide")
st.title("📌 微信群知识库 & 共创 Q&A")

# 选项卡划分板块
tab_qa, tab_rules, tab_docs = st.tabs(["❓ 共创 Q&A", "📜 群规须知", "📁 资料与公告"])

with tab_qa:
    # 1. 提交新问题
    with st.expander("➕ 提问新问题"):
        new_q = st.text_input("问题标题", key="input_new_q")
        if st.button("发布问题"):
            if new_q.strip():
                supabase.table("questions").insert({"title": new_q.strip()}).execute()
                st.success("问题发布成功！")
                st.rerun()

    # 2. 提交新回答
    questions_res = supabase.table("questions").select("*").order("id", desc=True).execute()
    questions = questions_res.data or []

    if questions:
        with st.expander("✍️ 提交你的答案"):
            q_options = {q["id"]: q["title"] for q in questions}
            selected_qid = st.selectbox("选择问题", options=list(q_options.keys()), format_func=lambda x: q_options[x])
            author_name = st.text_input("你的昵称", key="input_author")
            answer_content = st.text_area("你的解答", key="input_content")
            if st.button("提交回答"):
                if author_name.strip() and answer_content.strip():
                    supabase.table("answers").insert({
                        "question_id": selected_qid,
                        "author": author_name.strip(),
                        "content": answer_content.strip(),
                        "upvotes": 0
                    }).execute()
                    st.success("回答提交成功！")
                    st.rerun()

        st.divider()

        # 3. 展示问题与点赞排序回答
        for q in questions:
            st.subheader(f"Q: {q['title']}")
            answers_res = supabase.table("answers").select("*").eq("question_id", q["id"]).order("upvotes", desc=True).execute()
            answers = answers_res.data or []

            if answers:
                best = answers[0]
                st.markdown(f"**👑 正式采纳答案**（由 **{best['author']}** 提供，赞同数: `{best['upvotes']}`）")
                st.info(best["content"])
                
                col1, _ = st.columns([1, 5])
                with col1:
                    if st.button(f"👍 赞同 ({best['upvotes']})", key=f"btn_best_{best['id']}"):
                        supabase.table("answers").update({"upvotes": best["upvotes"] + 1}).eq("id", best["id"]).execute()
                        st.rerun()

                # 次高赞回答折叠展示
                if len(answers) > 1:
                    with st.expander(f"查看其余 {len(answers) - 1} 条备选回答"):
                        for alt in answers[1:]:
                            st.markdown(f"--- \n**{alt['author']}**（赞同数: `{alt['upvotes']}`）：")
                            st.write(alt["content"])
                            if st.button(f"👍 赞同 ({alt['upvotes']})", key=f"btn_alt_{alt['id']}"):
                                supabase.table("answers").update({"upvotes": alt["upvotes"] + 1}).eq("id", alt["id"]).execute()
                                st.rerun()
            else:
                st.caption("暂无回答，欢迎点击上方展开栏提交解答。")
    else:
        st.info("当前还没有问题，点击上方“提问新问题”添加第一条。")

with tab_rules:
    st.markdown("""
    ### 📜 群规须知
    1. 保持文明友善，禁止发布人身攻击言论。
    2. 禁止未经许可发布广告与引流链接。
    3. 群内文件与共创内容供内部交流使用。
    """)

with tab_docs:
    st.markdown("""
    ### 📁 常用资料与活动计划
    - **本期活动**：详见群置顶通知。
    - **文件汇总**：可在此处附上各类公开文档网盘链接。
    """)
