import streamlit as st

def offers_section(review_count):
    st.header("🎁 Special Offers")
    st.info(f"You have submitted {review_count} review(s).")
    if review_count >= 10:
        st.success("🎉 Congratulations! Here's your BookMyShow coupon: **CINE10-OFF**")
        st.markdown("Use it to get **10% OFF** on your next movie rental!")
    else:
        st.warning("Submit 10 reviews to unlock your discount!")
