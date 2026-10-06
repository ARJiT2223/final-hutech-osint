import streamlit as st
import duckdb

st.set_page_config(page_title="Hitek Data Lookup", page_icon="🔍")
st.title("🔍 Hitek Data Lookup")
st.write("Mobile number daalo aur details nikalo (bina 79GB download kiye).")

@st.cache_resource
def get_connection():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET memory_limit = '700MB';")
    con.execute("SET preserve_insertion_order = false;")
    con.execute("SET threads = 2;")
    return con

con = get_connection()

# Saari 20 files (alt 0-9 + final 0-9)
BASE_URL = "https://huggingface.co/buckets/CutehackX/hitek-data-bucket/resolve/"
ALT_FILES = [f"alt_master_shard_{i}.parquet" for i in range(10)]
FINAL_FILES = [f"final_master_shard_{i}.parquet" for i in range(10)]
ALT_URLS = [BASE_URL + f for f in ALT_FILES]
FINAL_URLS = [BASE_URL + f for f in FINAL_FILES]

# Column names (agar actual file me alag hain to yahan change kar)
COLUMNS = ["mobile", "name", "fname", "address", "alt", "circle", "id", "email"]

mobile_input = st.text_input("Mobile number (jaise 8840367739):", placeholder="10 digit number")

if st.button("Search karo"):
    if not mobile_input.strip():
        st.warning("Bhai, pehle number daal.")
    else:
        with st.spinner("Dhundh raha hoon... thoda time lag sakta hai."):
            try:
                result = None

                # Pehle alt_master me dhundh (fast, chhoti files)
                query_alt = f"""
                    SELECT * FROM read_parquet({ALT_URLS})
                    WHERE CAST("mobile" AS VARCHAR) = '{mobile_input}'
                    LIMIT 1;
                """
                try:
                    result = con.execute(query_alt).fetchall()
                except Exception:
                    result = None

                # Agar alt me na mile, toh final_master me dhundh
                if not result:
                    query_final = f"""
                        SELECT * FROM read_parquet({FINAL_URLS})
                        WHERE CAST("mobile" AS VARCHAR) = '{mobile_input}'
                        LIMIT 1;
                    """
                    try:
                        result = con.execute(query_final).fetchall()
                    except Exception:
                        result = None

                if not result:
                    st.error("❌ No result found for this number")
                else:
                    # Column names nikaalo
                    cols = [desc[0] for desc in con.description]
                    data = dict(zip(cols, result[0]))

                    # Null aur bytes handle karo
                    for k, v in data.items():
                        if v is None or str(v).lower() == "null":
                            data[k] = None
                        elif isinstance(v, bytes):
                            data[k] = v.decode("utf-8", errors="ignore")
                        else:
                            data[k] = str(v)

                    st.success("✅ Number mil gaya!")
                    st.json(data)

                    st.subheader("📋 Details:")
                    for k, v in data.items():
                        st.write(f"**{k}**: {v}")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                st.info("Lagta hai memory ya URL ka issue hai. Thoda wait karke phir try karo.")
