import os, re

nav_old = '''    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")'''

nav_new = '''    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")
    page = st.selectbox("🧭 Go to Page", [
        "🗺️ National View",
        "📊 State Analysis",
        "🏘️ District Explorer",
        "👥 Gender Analysis",
        "💰 Balance Analysis",
        "🤖 ML Insights",
        "📄 Policy Brief",
        "ℹ️ About"
    ])
    page_map = {
        "🗺️ National View": "pages/1_National_View.py",
        "📊 State Analysis": "pages/2_State_Analysis.py",
        "🏘️ District Explorer": "pages/3_District_View.py",
        "👥 Gender Analysis": "pages/4_Gender_Analysis.py",
        "💰 Balance Analysis": "pages/5_Balance_Analysis.py",
        "🤖 ML Insights": "pages/6_ML_Insights.py",
        "📄 Policy Brief": "pages/7_Policy_Brief.py",
        "ℹ️ About": "pages/8_About.py"
    }
    if st.button("Go ➜"):
        st.switch_page(page_map[page])
    st.markdown("---")'''

for fname in os.listdir('pages'):
    if fname.endswith('.py'):
        fpath = os.path.join('pages', fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        if '🧭 Go to Page' not in content and '🏠 Back to Home' in content:
            content = content.replace(nav_old, nav_new, 1)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {fname}')

print('Done!')