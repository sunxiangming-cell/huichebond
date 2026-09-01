import streamlit as st
from supabase import create_client

# 从 Streamlit Secrets 读取凭证
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)

st.set_page_config(page_title="微信群知识库 & 共创 Q&A", layout="wide")

# --- 初始化点赞记录，防止当前设备重复刷票 ---
if "voted_answers" not in st.session_state:
    st.session_state.voted_answers = set()

# --- 侧边栏管理员入口 ---
with st.sidebar:
    st.markdown("### ⚙️ 管理员入口")
    # 这里从 Secrets 读取密码，如果没配置默认是 888888
    admin_pwd = st.text_input("输入管理密码以启用删帖功能", type="password")
    is_admin = (admin_pwd == st.secrets.get("ADMIN_PASSWORD", "888888"))
    if is_admin:
        st.success("管理员身份已验证：高级管理模式开启")

st.title("📌 汇车退债交流主页 & 共创 Q&A")

# --- 新增了 tab_feedback ---
tab_qa, tab_rules, tab_docs, tab_feedback = st.tabs(["❓ 共创 Q&A", "📜 群规须知", "📁 资料与公告", "💡 给开发者提建议"])

with tab_qa:
    search_kw = st.text_input("🔍 搜索相关问题...")
    
    with st.expander("➕ 提问新问题"):
        new_q = st.text_input("问题标题", key="input_new_q")
        if st.button("发布问题"):
            if new_q.strip():
                supabase.table("questions").insert({"title": new_q.strip()}).execute()
                st.success("问题发布成功！")
                st.rerun()

    # 查询问题并应用搜索过滤
    questions_res = supabase.table("questions").select("*").order("id", desc=True).execute()
    questions = questions_res.data or []
    
    if search_kw:
        questions = [q for q in questions if search_kw.lower() in q["title"].lower()]

    if questions:
        with st.expander("✍️ 提交你的答案"):
            q_options = {q["id"]: q["title"] for q in questions}
            selected_qid = st.selectbox("选择问题", options=list(q_options.keys()), format_func=lambda x: q_options[x])
            author_name = st.text_input("你的昵称 (真实姓名/群昵称 + 持有张数)", key="input_author")
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

        # 展示问题与回答
        for q in questions:
            col_q1, col_q2 = st.columns([8, 1])
            with col_q1:
                st.subheader(f"Q: {q['title']}")
            with col_q2:
                # 管理员可以删除整个问题（级联删除所有相关回答）
                if is_admin and st.button("🗑️ 删题", key=f"del_q_{q['id']}"):
                    supabase.table("questions").delete().eq("id", q["id"]).execute()
                    st.rerun()

            answers_res = supabase.table("answers").select("*").eq("question_id", q["id"]).order("upvotes", desc=True).execute()
            answers = answers_res.data or []

            if answers:
                best = answers[0]
                st.markdown(f"**👑 正式采纳答案**（由 **{best['author']}** 提供，赞同数: `{best['upvotes']}`）")
                st.info(best["content"])
                
                # 正式答案的点赞与删除按钮
                col_btn, col_del, _ = st.columns([2, 2, 4])
                with col_btn:
                    is_voted = best["id"] in st.session_state.voted_answers
                    # 已点过赞则禁用按钮
                    if st.button(f"👍 赞同 ({best['upvotes']})", key=f"btn_best_{best['id']}", disabled=is_voted):
                        supabase.table("answers").update({"upvotes": best["upvotes"] + 1}).eq("id", best["id"]).execute()
                        st.session_state.voted_answers.add(best["id"])
                        st.rerun()
                with col_del:
                    if is_admin and st.button("🗑️ 删答", key=f"del_a_{best['id']}"):
                        supabase.table("answers").delete().eq("id", best["id"]).execute()
                        st.rerun()

                # 次高赞回答展示
                if len(answers) > 1:
                    with st.expander(f"查看其余 {len(answers) - 1} 条备选回答"):
                        for alt in answers[1:]:
                            st.markdown(f"--- \n**{alt['author']}**（赞同数: `{alt['upvotes']}`）：")
                            st.write(alt["content"])
                            
                            col_alt_btn, col_alt_del, _ = st.columns([2, 2, 4])
                            with col_alt_btn:
                                is_alt_voted = alt["id"] in st.session_state.voted_answers
                                if st.button(f"👍 赞同 ({alt['upvotes']})", key=f"btn_alt_{alt['id']}", disabled=is_alt_voted):
                                    supabase.table("answers").update({"upvotes": alt["upvotes"] + 1}).eq("id", alt["id"]).execute()
                                    st.session_state.voted_answers.add(alt["id"])
                                    st.rerun()
                            with col_alt_del:
                                if is_admin and st.button("🗑️ 删答", key=f"del_a_{alt['id']}"):
                                    supabase.table("answers").delete().eq("id", alt["id"]).execute()
                                    st.rerun()
            else:
                st.caption("暂无回答，欢迎点击上方展开栏提交解答。")
    else:
        st.info("当前还没有问题，或者没有搜到相关内容。")

with tab_rules:
    st.markdown("""
    ### 📌 汇车退债交流主页 · 群规与共创指南

    #### 一、 平台定位与功能机制
    本平台旨在为「汇车退债」全体持有人提供透明、有序、去中心化的信息共享与争议共识空间：
    1. **共创 Q&A 机制**：
       - 任何持有人均可就退债维权、重整进展、清偿方案等提交疑问。
       - 针对争议问题，所有持有人均可贡献独立解答；通过点赞（👍）推举认同度最高的内容成为**正式置顶答案**。
       - 次高赞方案将在备选区展开留存，确保多元视角与全面考量。
    2. **资料与公告汇总**：沉淀官方公告、重整时间表、维权模板与会议纪要，避免微信群刷屏被淹没。

    ---

    #### 二、 发帖与命名规范（实名认证与诚信原则）
    1. **昵称命名格式**：发帖与提交解答时，昵称请统一规范为 **`真实姓名/群昵称 + 持有张数`**（例如：`张三(1200张)`）。
       - 未按规则署名或冒用他人身份的内容，管理员有权无预警清理，以维护真实持有人交流环境。
    2. **理性探讨**：债权处置利益相关复杂，请就事论事、摆事实讲证据，严禁无事实依据的恶意造谣、恐慌情绪煽动或人身攻击。
    3. **严禁广告违规**：严禁发布非官方维权收费群、商业推广、恶意引流、政治敏感言论及违法违规信息。

    ---

    #### 三、 免责声明与风险提示
    1. 本平台所有内容均由持有人自发贡献与投票筛选，**不构成任何法律意见、投资建议或最终官方结论**。
    2. 重整及退债相关事宜请以司法机关、管理人及上市公司发布的**官方正式公告**为准。
    3. 平台不采集任何敏感隐私（身份证号、证券账户密码、持仓截图原图等），请群友注意保护个人资产安全。
    """)

with tab_docs:
    st.markdown("""
    ### 📁 常用资料与活动计划
    - **本期活动**：详见群置顶通知。
    - **文件汇总**：可在此处附上各类公开文档网盘链接。
    """)

with tab_feedback:
    st.markdown("### 💡 给开发者提建议")
    st.info("如果您对本网站有任何功能建议、排版改进或发现了 Bug，欢迎在此提交。")
    
    with st.form("feedback_form"):
        fb_content = st.text_area("您的建议内容...")
        if st.form_submit_button("提交建议"):
            if fb_content.strip():
                supabase.table("feedback").insert({"content": fb_content.strip()}).execute()
                st.success("感谢您的反馈，建议已提交！")
                
    if is_admin:
        st.divider()
        st.markdown("#### 🔧 建议列表 (仅管理员可见)")
        fb_res = supabase.table("feedback").select("*").order("id", desc=True).execute()
        feedbacks = fb_res.data or []
        if feedbacks:
            for fb in feedbacks:
                st.caption(f"📅 提交时间: {fb['created_at'][:10]}")
                st.write(fb['content'])
                st.markdown("---")
        else:
            st.caption("暂无新建议。")
