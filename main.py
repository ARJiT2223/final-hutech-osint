import streamlit as st
import duckdb

# 1. DuckDB ko 1GB RAM ke liye optimize karo
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("SET memory_limit = '800MB';")  # 1GB RAM me safe rahe
con.execute("SET preserve_insertion_order = false;")  # memory aur kam
con.execute("SET threads = 2;")  # 2 threads, zyada nahi

# 2. Teri saari 20 files (alt 0-9 + final 0-9)
BASE_URL = "https://huggingface.co/buckets/CutehackX/hitek-data-bucket/resolve/"
FILES = [
    # Alt Master Shards (0 se 9 tak)
    "alt_master_shard_0.parquet",
    "alt_master_shard_1.parquet",
    "alt_master_shard_2.parquet",
    "alt_master_shard_3.parquet",
    "alt_master_shard_4.parquet",
    "alt_master_shard_5.parquet",
    "alt_master_shard_6.parquet",
    "alt_master_shard_7.parquet",
    "alt_master_shard_8.parquet",
    "alt_master_shard_9.parquet",
    # Final Master Shards (0 se 9 tak)
    "final_master_shard_0.parquet",
    "final_master_shard_1.parquet",
    "final_master_shard_2.parquet",
    "final_master_shard_3.parquet",
    "final_master_shard_4.parquet",
    "final_master_shard_5.parquet",
    "final_master_shard_6.parquet",
    "final_master_shard_7.parquet",
    "final_master_shard_8.parquet",
    "final_master_shard_9.parquet",
]

# 3. Poori file list ke URLs banao
FILE_URLS = [BASE_URL + f for f in FILES]

# 4. Streamlit UI Setup
st.set_page_config(page_title="Hitek Data Lookup", page_icon="🔍")
st.title("🔍 Hitek Data Lookup")
st.write("Mobile number daalo aur details nikalo (bina 79GB download kiye).")

mobile_input = st.text_input("Mobile number (jaise 8840367739):", placeholder="10 digit number")

if st.button("Search karo"):
    if not mobile_input:
        st.warning("Bhai, pehle number daal.")
    else:
        with st.spinner("Dhundh raha hoon... thoda time lag sakta hai."):
            try:
                # 5. Query: saari files me mobile exact match, ya alt/address me partial
                query = f"""
                    SELECT mobile, name, fname, address, alt, circle, id, email
                    FROM read_parquet({FILE_URLS})
                    WHERE CAST("mobile" AS VARCHAR) = '{mobile_input}'
                       OR CAST("alt" AS VARCHAR) LIKE '%{mobile_input}%'
                       OR CAST("address" AS VARCHAR) LIKE '%{mobile_input}%'
                    LIMIT 1;
                """
                
                result = con.execute(query).fetchall()

                if not result:
                    st.error("❌ No result found for this number")
                else:
                    # 6. Result ko dictionary me convert karo
                    columns = ["mobile", "name", "fname", "address", "alt", "circle", "id", "email"]
                    data = dict(zip(columns, result[0]))

                    st.success("✅ Number mil gaya!")
                    
                    # 7. Sundar formatted JSON dikhao
                    st.json(data)

                    # 8. Extra: Har field alag se bhi dikhao
                    st.subheader("📋 Details:")
                    for key, value in data.items():
                        st.write(f"**{key.capitalize()}**: {value}")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                st.info("Lagta hai memory ya URL ka issue hai. Thoda wait karke phir try karo.")
