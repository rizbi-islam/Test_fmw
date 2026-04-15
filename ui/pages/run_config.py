import ui._pathfix  # noqa
import streamlit as st
from ui.state import init_state, get_config, save_config


def render():
    init_state()
    config = get_config()
    st.title("⚙️ Run Configuration")
    st.caption("Configure all settings. Changes are saved to config/config.yaml.")
    st.divider()

    # ── Driver ────────────────────────────────────────────────
    st.subheader("🚗 Driver Settings")
    dc1, dc2, dc3 = st.columns(3)
    config.setdefault("driver", {})
    config["driver"]["default"] = dc1.selectbox(
        "Driver", ["selenium","playwright"],
        index=["selenium","playwright"].index(config["driver"].get("default","selenium")))
    config["driver"]["browser"] = dc2.selectbox(
        "Browser", ["chrome","firefox","edge"],
        index=["chrome","firefox","edge"].index(config["driver"].get("browser","chrome")))
    config["driver"]["headless"] = dc3.checkbox(
        "Headless", value=config["driver"].get("headless", False))
    dc4, dc5 = st.columns(2)
    config["driver"]["implicit_wait"]     = dc4.number_input("Implicit Wait (s)",    min_value=1, max_value=60,  value=int(config["driver"].get("implicit_wait",10)))
    config["driver"]["page_load_timeout"] = dc5.number_input("Page Load Timeout (s)", min_value=5, max_value=120, value=int(config["driver"].get("page_load_timeout",30)))
    st.divider()

    # ── Data Source ───────────────────────────────────────────
    st.subheader("💾 Data Source")
    config.setdefault("data", {})
    config["data"]["default_provider"] = st.selectbox(
        "Default Provider", ["excel","sqlite","mysql","json"],
        index=["excel","sqlite","mysql","json"].index(config["data"].get("default_provider","excel")))
    if config["data"]["default_provider"] == "excel":
        config["data"].setdefault("excel",{})
        ep1, ep2 = st.columns(2)
        config["data"]["excel"]["test_suite_path"] = ep1.text_input(
            "Test Suite Path", value=config["data"]["excel"].get("test_suite_path","assets/templates/test_suite.xlsx"))
        config["data"]["excel"]["suite_sheet"] = ep2.text_input(
            "Suite Sheet", value=config["data"]["excel"].get("suite_sheet","TestSuite"))
    elif config["data"]["default_provider"] == "sqlite":
        config["data"].setdefault("sqlite",{})
        config["data"]["sqlite"]["db_path"] = st.text_input(
            "SQLite DB Path", value=config["data"]["sqlite"].get("db_path","data/kwaf_test.db"))
    elif config["data"]["default_provider"] == "mysql":
        config["data"].setdefault("mysql",{})
        mc1,mc2,mc3 = st.columns(3)
        config["data"]["mysql"]["host"]     = mc1.text_input("Host",     value=config["data"]["mysql"].get("host","localhost"))
        config["data"]["mysql"]["port"]     = mc2.number_input("Port",   value=int(config["data"]["mysql"].get("port",3306)), min_value=1)
        config["data"]["mysql"]["database"] = mc3.text_input("Database", value=config["data"]["mysql"].get("database","kwaf_db"))
        mc4,mc5 = st.columns(2)
        config["data"]["mysql"]["username"] = mc4.text_input("Username", value=config["data"]["mysql"].get("username","root"))
        config["data"]["mysql"]["password"] = mc5.text_input("Password", value=config["data"]["mysql"].get("password",""), type="password")
    st.divider()

    # ── OTP ───────────────────────────────────────────────────
    st.subheader("📱 OTP Settings")
    config.setdefault("otp",{})
    config["otp"]["default"] = st.selectbox(
        "OTP Handler", ["mock","firebase","gmail"],
        index=["mock","firebase","gmail"].index(config["otp"].get("default","mock")))
    if config["otp"]["default"] == "mock":
        config["otp"].setdefault("mock",{})
        config["otp"]["mock"]["otp_value"] = st.text_input(
            "Static OTP Value", value=config["otp"]["mock"].get("otp_value","123456"))
    elif config["otp"]["default"] == "firebase":
        config["otp"].setdefault("firebase",{})
        fo1,fo2 = st.columns(2)
        config["otp"]["firebase"]["credentials_path"] = fo1.text_input(
            "Credentials JSON", value=config["otp"]["firebase"].get("credentials_path","config/firebase_credentials.json"))
        config["otp"]["firebase"]["database_url"] = fo2.text_input(
            "Database URL", value=config["otp"]["firebase"].get("database_url",""))
        config["otp"]["firebase"]["otp_path"] = st.text_input(
            "OTP Path", value=config["otp"]["firebase"].get("otp_path","otp/device1"))
    elif config["otp"]["default"] == "gmail":
        config["otp"].setdefault("gmail",{})
        go1,go2 = st.columns(2)
        config["otp"]["gmail"]["email"]          = go1.text_input("Gmail", value=config["otp"]["gmail"].get("email",""))
        config["otp"]["gmail"]["app_password"]   = go2.text_input("App Password", value=config["otp"]["gmail"].get("app_password",""), type="password")
        config["otp"]["gmail"]["subject_filter"] = st.text_input("Subject Filter", value=config["otp"]["gmail"].get("subject_filter","OTP"))
    st.divider()

    # ── CAPTCHA ───────────────────────────────────────────────
    st.subheader("🤖 CAPTCHA Settings")
    config.setdefault("captcha",{})
    config["captcha"]["default"] = st.selectbox(
        "CAPTCHA Strategy", ["bypass","twocaptcha","manual"],
        index=["bypass","twocaptcha","manual"].index(config["captcha"].get("default","bypass")))
    if config["captcha"]["default"] == "twocaptcha":
        config["captcha"].setdefault("twocaptcha",{})
        tc1,tc2 = st.columns(2)
        config["captcha"]["twocaptcha"]["api_key"] = tc1.text_input(
            "API Key", value=config["captcha"]["twocaptcha"].get("api_key",""), type="password")
        config["captcha"]["twocaptcha"]["captcha_type"] = tc2.selectbox(
            "Type", ["recaptchav2","recaptchav3","hcaptcha","image"],
            index=["recaptchav2","recaptchav3","hcaptcha","image"].index(
                config["captcha"]["twocaptcha"].get("captcha_type","recaptchav2")))
    st.divider()

    # ── Execution ─────────────────────────────────────────────
    st.subheader("🏃 Execution Settings")
    config.setdefault("execution",{})
    ex1,ex2,ex3 = st.columns(3)
    config["execution"]["mode"] = ex1.selectbox(
        "Mode", ["sequential","parallel"],
        index=["sequential","parallel"].index(config["execution"].get("mode","sequential")))
    config["execution"]["retry_on_failure"] = ex2.number_input(
        "Retry on Failure", min_value=0, max_value=5,
        value=int(config["execution"].get("retry_on_failure",1)))
    config["execution"]["stop_on_first_failure"] = ex3.checkbox(
        "Stop on First Failure", value=config["execution"].get("stop_on_first_failure",False))
    config["execution"]["screenshot_on_failure"] = st.checkbox(
        "Screenshot on Failure", value=config["execution"].get("screenshot_on_failure",True))
    st.divider()

    # ── Environment ───────────────────────────────────────────
    st.subheader("🌍 Environment")
    config.setdefault("environment",{})
    en1,en2 = st.columns(2)
    config["environment"]["name"] = en1.selectbox(
        "Environment", ["local","staging","production"],
        index=["local","staging","production"].index(config["environment"].get("name","local")))
    config["environment"]["base_url"] = en2.text_input(
        "Base URL", value=config["environment"].get("base_url",""),
        placeholder="https://your-app.com")
    st.divider()

    if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
        try:
            save_config(config)
            st.session_state.kwaf_config = config
            st.success("✅ Configuration saved to config/config.yaml")
        except Exception as e:
            st.error(f"Save failed: {e}")
