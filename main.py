import streamlit as st
from supabase import create_client  

# 1. Database Connection
# Make sure these match your Streamlit Secrets or environment variables
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Monthly Count Tracker", page_icon="📚")
st.title("Monthly Count Tracker")

# 2. Select the Table/Group
group = st.selectbox("Select Group", ["श्री विष्णु सहस्त्रनाम स्तोत्र", "श्री व्यंकटेश स्तोत्र"])
dropdown_dict = {"श्री विष्णु सहस्त्रनाम स्तोत्र": "Vishnu", "श्री व्यंकटेश स्तोत्र": "Venkatesh"}
group = dropdown_dict.get(group, "Vishnu")
table_name = f"monthly_count_table_{group.lower()}" # appended table name 

# 3. Simple Login
username_input = st.text_input("Enter Username")
username_pass = st.text_input("Enter Password", type="password")

if username_input and username_pass:
    # Fetch data for this specific user from the chosen table
    response = supabase.table(table_name).select("*").eq("username", username_input).execute()
    
    if response.data:
        user_data = response.data[0]
        stored_password = user_data.get("password_hash")

        # 4. Password Verification
        if username_pass == stored_password:
            st.success(f"Welcome back, {username_input}!")
            st.success(f"Logged into {group}'s list as {username_input}")
            
            # 4. Display Individual Counters
            people = ["Dhananjay", "Ujawala", "Archana", "Anju", "Chhaya"]
            
            st.subheader("Current Counts")
            # Create a nice layout for the people
            cols = st.columns(len(people))

            # reset
            if st.button("🚨 Reset All Counts to Zero", use_container_width=True):
                # 1. Prepare the full dictionary of zeros
                reset_data = {p.lower(): 0 for p in people}
                
                # 2. Update the WHOLE row in one single command
                supabase.table(table_name).update(reset_data).eq("username", username_input).execute()
                
                # 3. Notify and Rerun
                st.warning("All counts have been reset in the database!")
                st.rerun() # This will force a fresh fetch of the new 0 values
                            
            for i, person in enumerate(people):
                person = person.lower()
                current_val = user_data.get(person, 0)
                cols[i].metric(person, current_val)
                # 5. Increment Logic
                # We use a unique key for each button to avoid Streamlit errors
                try:
                    if cols[i].button(f"+1 for {person}", key=f"btn_{person}"):
                        new_val = current_val + 1
                        # Update the database for that specific column
                        supabase.table(table_name).update({person: new_val}).eq("username", username_input).execute()
                        st.toast(f"Updated {person} to {new_val}!")
                        st.rerun()
                        
                except Exception as e:
                    st.write(f"{e}, Update failed!")

                
    else:
        st.error("Username not found in this group's table.")

# Optional: Add a "View All" section to see everyone's progress
if st.checkbox("Show Overall Group Status"):
    all_data = supabase.table(table_name).select("*").execute()
    if all_data.data:
        st.table(all_data.data)