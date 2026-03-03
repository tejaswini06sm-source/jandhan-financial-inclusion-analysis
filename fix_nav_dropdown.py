import os, re

nav_old = '''    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")'''

nav_new = '''    st.page_link("app.py", label="🏠 Back to Home")
    st.markdown("---")
    pages = {
        "🗺️ National View": "pages/1_National_View.py",
        "📊 State Analysis": "pages/2_State_Analysis.py",
        "🏘️ District Explorer": "pages/3_District_View.py",
        "👥 Gender Analysis": "pages/4_Gender_Analysis.py",
        "💰 Balance Analysis": "pages/5_Balance_Analysis.py",
        "🤖 ML Insights": "pages/6_ML_Insights.py",
        "📄 Policy Brief": "pages/7_Policy_Brief.py",
        "ℹ️ About": "pages/8_About.py"
    }
    selected_page = st.selectbox("📂 Navigate", list(pages.keys()))
    if selected_page:
        st.switch_page(pages[selected_page])
    st.markdown("---")'''

for fname in os.listdir('pages'):
    if fname.endswith('.py'):
        fpath = os.path.join('pages', fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove old Go button version first
        content = re.sub(
            r'    pages = \{.*?st\.markdown\("---"\)',
            '',
            content,
            flags=re.DOTALL
        )
        # Remove old page_map + button version
        content = re.sub(
            r'    page = st\.selectbox.*?st\.markdown\("---"\)',
            '',
            content,
            flags=re.DOTALL
        )
        
        if '📂 Navigate' not in content and '🏠 Back to Home' in content:
            content = content.replace(nav_old, nav_new, 1)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {fname}')

print('Done!')